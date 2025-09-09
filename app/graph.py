from typing import Dict
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_openai import ChatOpenAI
def build_graph(llm: ChatOpenAI):
    def call_llm(state: MessagesState) -> Dict:
        ai_message = llm.invoke(state["messages"]); return {"messages": [ai_message]}
    builder = StateGraph(MessagesState)
    builder.add_node("llm", call_llm); builder.add_edge(START, "llm"); builder.add_edge("llm", END)
    return builder.compile()
