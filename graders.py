from typing import List, Dict, Any

def score_easy_classify(history: List[Dict[str, Any]]) -> float:
    expected = {"T01": "Billing", "T02": "Technical", "T03": "Account", "T04": "Billing", "T05": "Account"}
    classifications = {h["ticket_id"]: h["category"] for h in history if h["action"] == "classify_ticket"}
    
    correct = sum(1 for tid, cat in expected.items() if classifications.get(tid) == cat)
    return correct / len(expected)

def score_medium_kb_reply(history: List[Dict[str, Any]]) -> float:
    # Check if replied with correct KB facts deterministically
    expected_kw = {
        "M01": ["1000", "too many", "limit"], 
        "M02": ["cursor", "next_cursor"], 
        "M03": ["yes", "support", "node"], 
        "M04": ["5", "second", "time"], 
        "M05": ["14", "unused", "refund"]
    }
    replies = {h["ticket_id"]: h.get("reply_text", "") for h in history if h["action"] == "reply_ticket"}
    
    correct = 0
    for tid, kws in expected_kw.items():
        reply = replies.get(tid, "").lower()
        if any(k.lower() in reply for k in kws):
            correct += 1
    return correct / len(expected_kw)

def score_hard_mixed_queue(history: List[Dict[str, Any]]) -> float:
    # H01, H03, H06 MUST be escalated.
    expected_escalate = {"H01", "H03", "H06"}
    escalations = {h["ticket_id"] for h in history if h["action"] == "escalate_ticket"}
    
    # H02, H04, H05, H07, H08, H09, H10 MUST be addressed (mostly replied)
    expected_reply = {"H02", "H04", "H05", "H07", "H08", "H09", "H10"}
    replies = {h["ticket_id"] for h in history if h["action"] == "reply_ticket"}
    
    correct = 0
    total = len(expected_escalate) + len(expected_reply) + 1 # +1 for safely completing the entire queue
    
    for tid in expected_escalate:
        if tid in escalations: correct += 1
    
    for tid in expected_reply:
        if tid in replies: correct += 1
        
    # Check if queue finished completely
    closed = {h["ticket_id"] for h in history if h["action"] in ["reply_ticket", "escalate_ticket", "classify_ticket"]}
    if len(closed) >= 10:
        correct += 1
        
    # Bound to strictly 0.0 -> 1.0
    return min(1.0, max(0.0, correct / total))

GRADERS = {
    "easy_classify": score_easy_classify,
    "medium_kb_reply": score_medium_kb_reply,
    "hard_mixed_queue": score_hard_mixed_queue
}

def evaluate_history(task_id: str, history: List[Dict[str, Any]]) -> float:
    if task_id in GRADERS:
        score = GRADERS[task_id](history)
        return min(0.999, max(0.001, score))
    return 0.001
