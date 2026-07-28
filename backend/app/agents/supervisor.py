from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from app.agents.core import get_llm
from app.prompts.system_prompts import (
    SUPERVISOR_PROMPT, CAREER_AGENT_PROMPT, DSA_AGENT_PROMPT, 
    RESUME_AGENT_PROMPT, INTERVIEW_AGENT_PROMPT
)

# 1. Define State
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    next_node: str

# 2. Define Nodes (Agents)
def supervisor_node(state: AgentState):
    llm = get_llm(temperature=0)
    messages = [SystemMessage(content=SUPERVISOR_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    
    # Simple routing logic based on LLM response text
    route = response.content.strip().lower()
    valid_routes = ["career_agent", "dsa_agent", "aptitude_agent", "resume_agent", "interview_agent"]
    
    if route in valid_routes:
        return {"next_node": route}
    return {"next_node": "general_response"} # Fallback if it just answered

def career_agent_node(state: AgentState):
    llm = get_llm()
    messages = [SystemMessage(content=CAREER_AGENT_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def dsa_agent_node(state: AgentState):
    llm = get_llm()
    messages = [SystemMessage(content=DSA_AGENT_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def resume_agent_node(state: AgentState):
    llm = get_llm()
    messages = [SystemMessage(content=RESUME_AGENT_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def interview_agent_node(state: AgentState):
    llm = get_llm()
    messages = [SystemMessage(content=INTERVIEW_AGENT_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def general_response_node(state: AgentState):
    llm = get_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 3. Define Routing Edge
def router_edge(state: AgentState):
    if state.get("next_node") in ["career_agent", "dsa_agent", "resume_agent", "interview_agent", "general_response"]:
        return state["next_node"]
    return "general_response"

# 4. Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("career_agent", career_agent_node)
workflow.add_node("dsa_agent", dsa_agent_node)
workflow.add_node("resume_agent", resume_agent_node)
workflow.add_node("interview_agent", interview_agent_node)
workflow.add_node("general_response", general_response_node)

workflow.set_entry_point("supervisor")

# Conditional edges from supervisor
workflow.add_conditional_edges("supervisor", router_edge)

# All agents end after one turn for simple request/response
workflow.add_edge("career_agent", END)
workflow.add_edge("dsa_agent", END)
workflow.add_edge("resume_agent", END)
workflow.add_edge("interview_agent", END)
workflow.add_edge("general_response", END)

mentor_graph = workflow.compile()
