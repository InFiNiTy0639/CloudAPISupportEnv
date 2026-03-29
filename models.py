from pydantic import BaseModel, Field
from typing import Optional, Literal, List

class Ticket(BaseModel):
    ticket_id: str
    subject: str
    body: str
    priority: Literal["Low", "Medium", "High", "Critical"] = Field(description="Priority of the ticket.")

class Observation(BaseModel):
    current_ticket: Optional[Ticket] = Field(description="The current ticket being handled. None if queue empty.")
    tickets_remaining: int = Field(description="Number of tickets left in the queue.")
    kb_search_results: Optional[str] = Field(description="Results from the last Knowledge Base search.")
    last_action_status: str = Field(description="Status or error message from the previous action.")
    conversation_history: List[str] = Field(description="History of actions taken on the current ticket.")

class Action(BaseModel):
    action_type: Literal["classify_ticket", "search_kb", "reply_ticket", "escalate_ticket", "close_ticket"] = Field(description="Type of action to perform.")
    ticket_id: Optional[str] = Field(None, description="ID of the ticket.")
    category: Optional[Literal["Billing", "Technical", "Account", "Other"]] = Field(None, description="For classifying.")
    reply_text: Optional[str] = Field(None, description="Response message to the user.")
    reason: Optional[str] = Field(None, description="Reason for escalation.")
    query: Optional[str] = Field(None, description="Query for KB search.")

class Reward(BaseModel):
    score: float = Field(description="Reward signal typically between -1.0 and 1.0.")
    reason: str = Field(description="Reason for the reward.")
