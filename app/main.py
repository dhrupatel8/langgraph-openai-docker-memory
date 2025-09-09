import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ChatRequest, ChatResponse, ChatMessage
from .utils import to_lc_messages, get_llm, load_session, save_session, ensure_session_id
from .graph import build_graph
app = FastAPI(title="LangGraph + OpenAI API (Memory)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
llm = get_llm(); compiled_graph = build_graph(llm)
@app.get("/", response_class=HTMLResponse)
async def index():
    here = os.path.join(os.path.dirname(__file__), "web", "index.html")
    with open(here, "r", encoding="utf-8") as f: return HTMLResponse(content=f.read())
@app.get("/graph.mmd", response_class=PlainTextResponse)
def graph_mermaid(): return compiled_graph.get_graph().draw_mermaid()
@app.get("/graph", response_class=HTMLResponse)
def graph_page():
    mmd = compiled_graph.get_graph().draw_mermaid()
    return f"""<!doctype html><html><head>
  <meta charset="utf-8" />
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({{ startOnLoad: true }});</script>
</head><body><div class="mermaid">{mmd}</div></body></html>"""
@app.get("/memory")
def get_memory(session_id: Optional[str] = Query(default=None)):
    sid = ensure_session_id(session_id); data = load_session(sid)
    return {"session_id": sid, "current": data.get("current", [])}
@app.get("/memory/archives")
def list_archives(session_id: Optional[str] = Query(default=None)):
    sid = ensure_session_id(session_id); data = load_session(sid)
    archives = [{"id": i, "size": len(a)} for i, a in enumerate(data.get("archives", []))]
    return {"session_id": sid, "archives": archives}
@app.get("/memory/archive/{archive_id}")
def get_archive(archive_id: int, session_id: Optional[str] = Query(default=None)):
    sid = ensure_session_id(session_id); data = load_session(sid)
    try: return {"session_id": sid, "archive_id": archive_id, "messages": data["archives"][archive_id]}
    except Exception: raise HTTPException(status_code=404, detail="Archive not found")
@app.post("/memory/archive")
def archive_current(session_id: Optional[str] = Query(default=None)):
    sid = ensure_session_id(session_id); data = load_session(sid)
    current = data.get("current", [])
    if current: data.setdefault("archives", []).append(current); data["current"] = []; save_session(sid, data)
    return {"session_id": sid, "archived": True, "archives_count": len(data.get("archives", []))}
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, session_id: Optional[str] = Query(default=None)):
    if not os.getenv("OPENAI_API_KEY"): raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")
    sid = ensure_session_id(session_id); data = load_session(sid)
    try:
        lc_msgs = to_lc_messages([m.model_dump() for m in req.messages])
        result = compiled_graph.invoke({"messages": lc_msgs})
        reply = ChatMessage(role="assistant", content=result["messages"][-1].content)
        transcript = req.messages + [reply]
        data["current"] = [m.model_dump() for m in transcript]; save_session(sid, data)
        return ChatResponse(message=reply, messages=transcript, session_id=sid)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
