from typing import TypedDict

from langgraph.graph import END, StateGraph


class State(TypedDict):
    task_id: str
    answer: str


def plan_node(state: State) -> State:
    return state


def execute_node(state: State) -> State:
    return state


workflow = StateGraph(State)
workflow.add_node("plan", plan_node)
workflow.add_node("execute", execute_node)
workflow.set_entry_point("plan")
workflow.add_edge("plan", "execute")
workflow.add_edge("execute", END)
compiled_graph = workflow.compile(checkpointer="postgres")
