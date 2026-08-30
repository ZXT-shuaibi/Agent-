from pydantic import BaseModel
from langchain_core.tools import tool


class TicketInput(BaseModel):
    ticket_id: str


@tool
def close_ticket(ticket_id: str) -> str:
    """Close a support ticket after approval."""
    return ticket_id
