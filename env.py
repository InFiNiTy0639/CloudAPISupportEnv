from typing import Any, Tuple, Dict
from models import Observation, Action, Reward
from tasks import get_task_data, KB_ARTICLES

class CustomerSupportEnv:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.tickets = []
        self.history = []
        self.current_ticket_index = 0
        self.kb_search_results = None
        self.last_action_status = ""
        self.conversation_history = []
        self.done = False
        self.steps = 0
        self.max_steps = 50
        self.invalid_actions = 0

    def reset(self) -> Observation:
        self.tickets = get_task_data(self.task_id)
        self.history = []
        self.current_ticket_index = 0
        self.kb_search_results = None
        self.last_action_status = "Environment initialized. Awaiting action."
        self.conversation_history = []
        self.done = False
        self.steps = 0
        self.invalid_actions = 0
        return self.state()

    def state(self) -> Observation:
        current_ticket = self.tickets[self.current_ticket_index] if self.current_ticket_index < len(self.tickets) else None
        return Observation(
            current_ticket=current_ticket,
            tickets_remaining=max(0, len(self.tickets) - self.current_ticket_index),
            kb_search_results=self.kb_search_results,
            last_action_status=self.last_action_status,
            conversation_history=self.conversation_history
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        self.steps += 1
        reward_score = 0.0
        reward_reason = ""
        info = {
            "ticket_resolved": False,
            "correct_action": False,
            "kb_used": False,
            "invalid_action": False
        }

        if self.done:
            return self.state(), Reward(score=0.0, reason="Episode done"), True, info
            
        if self.steps >= self.max_steps:
            self.done = True
            self.last_action_status = "Max steps reached."
            return self.state(), Reward(score=-1.0, reason="Failed to complete queue in time."), True, info

        current_ticket = self.tickets[self.current_ticket_index]
        tid = current_ticket.ticket_id

        # Ticket ID mismatch
        if action.action_type in ["classify_ticket", "reply_ticket", "escalate_ticket", "close_ticket"]:
            if action.ticket_id != tid:
                self.invalid_actions += 1
                self.last_action_status = f"Invalid action: Wrong ticket ID {action.ticket_id}."
                info["invalid_action"] = True
                return self.state(), Reward(score=-0.2, reason="Incorrect ticket ID."), self.done, info

        if action.action_type == "search_kb":
            q = (action.query or "").lower()
            results = [f"[{k}] {v}" for k, v in KB_ARTICLES.items() if q in k.lower() or q in v.lower()]
            if results:
                self.kb_search_results = "\n".join(results[:3])
                self.last_action_status = "KB search successful."
                reward_score = 0.1
                reward_reason = "Used KB effectively."
                info["correct_action"] = True
                info["kb_used"] = True
                self.conversation_history.append(f"Searched KB for '{q}'.")
            else:
                self.kb_search_results = "No results found."
                self.last_action_status = "KB search returned no results."
                reward_score = -0.05
                reward_reason = "Irrelevant KB search."
                self.conversation_history.append(f"Searched KB for '{q}' (No results).")

        elif action.action_type == "classify_ticket":
            if not action.category:
                self.invalid_actions += 1
                self.last_action_status = "Missing category for classification."
                reward_score = -0.2
            else:
                self.last_action_status = f"Classified as {action.category}."
                self.conversation_history.append(f"Classified: {action.category}")
                self.history.append({"ticket_id": tid, "action": "classify_ticket", "category": action.category})
                reward_score = 0.1
                reward_reason = "Classified ticket."
                info["correct_action"] = True

        elif action.action_type == "reply_ticket":
            if not action.reply_text:
                self.invalid_actions += 1
                self.last_action_status = "Reply text missing."
                reward_score = -0.2
            else:
                self.last_action_status = "Sent reply."
                self.conversation_history.append(f"Replied: {action.reply_text[:50]}...")
                self.history.append({"ticket_id": tid, "action": "reply_ticket", "reply_text": action.reply_text})
                reward_score = 0.2
                reward_reason = "Constructed a reply."
                info["correct_action"] = True

        elif action.action_type == "escalate_ticket":
            if not action.reason:
                self.invalid_actions += 1
                self.last_action_status = "Escalation reason missing."
                reward_score = -0.2
            else:
                self.last_action_status = f"Escalated: {action.reason}"
                self.conversation_history.append("Escalated to management.")
                self.history.append({"ticket_id": tid, "action": "escalate_ticket", "reason": action.reason})
                reward_score = 0.2
                reward_reason = "Escalated effectively."
                info["correct_action"] = True

        elif action.action_type == "close_ticket":
            # Must reply or escalate first
            has_acted = any(
                h["action"] in ["reply_ticket", "escalate_ticket", "classify_ticket"] 
                for h in self.history if h["ticket_id"] == tid
            )
            if not has_acted:
                self.invalid_actions += 1
                self.last_action_status = "Cannot close without taking action (reply, escalate, or classify)."
                reward_score = -0.3
                reward_reason = "Premature close."
                info["invalid_action"] = True
            else:
                self.current_ticket_index += 1
                self.kb_search_results = None
                self.conversation_history = []
                self.last_action_status = f"Closed ticket {tid}. Moved to next."
                info["ticket_resolved"] = True
                info["correct_action"] = True
                
                if self.current_ticket_index >= len(self.tickets):
                    self.done = True
                    self.last_action_status = "Queue empty. Done."
                    reward_score = 1.0 # Big reward for finishing
                    reward_reason = "Completed all tickets."
                else:
                    reward_score = 0.2
                    reward_reason = "Successfully resolved a ticket."

        else:
            self.invalid_actions += 1
            self.last_action_status = "Unknown action."
            reward_score = -0.2
            info["invalid_action"] = True

        if self.invalid_actions >= 10:
            self.done = True
            self.last_action_status = "Too many invalid actions. Episode terminated."
            reward_score = -1.0
            
        return self.state(), Reward(score=reward_score, reason=reward_reason), self.done, info
