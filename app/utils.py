import os, json, uuid, pathlib
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
load_dotenv(override=True)
ROLE_TO_MSG = {"system": SystemMessage,"user": HumanMessage,"assistant": AIMessage}
def to_lc_messages(pairs: List[dict]) -> List[BaseMessage]:
    out: List[BaseMessage] = []
    for p in pairs:
        role = p.get("role"); content = p.get("content", "")
        cls = ROLE_TO_MSG.get(role)
        if not cls: raise ValueError(f"Unknown role: {role}")
        out.append(cls(content=content))
    return out
def get_llm() -> ChatOpenAI:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
    return ChatOpenAI(model=model, temperature=temperature)
def _mem_dir() -> pathlib.Path:
    p = pathlib.Path(os.getenv("MEMORY_DIR", "/data")); p.mkdir(parents=True, exist_ok=True); return p
def _session_path(session_id: str) -> pathlib.Path: return _mem_dir() / f"{session_id}.json"
def load_session(session_id: str) -> Dict:
    path = _session_path(session_id)
    if path.exists():
        try: return json.loads(path.read_text(encoding="utf-8"))
        except Exception: pass
    return {"current": [], "archives": []}
def save_session(session_id: str, data: Dict) -> None:
    _session_path(session_id).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def ensure_session_id(session_id: Optional[str]) -> str:
    return session_id or uuid.uuid4().hex
