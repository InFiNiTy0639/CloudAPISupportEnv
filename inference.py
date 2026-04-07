import os
import time
import json
import random
from dotenv import load_dotenv

load_dotenv()
from env import CustomerSupportEnv
from tasks import TASKS
from graders import evaluate_history
from models import Action

random.seed(42)

def run_agent_on_task(task_id: str):
    print(f"\n{'='*50}")
    print(f"--- Running baseline for task: {task_id} ---")
    print(f"{'='*50}")
    print(f"[START] task={task_id}", flush=True)
    env = CustomerSupportEnv(task_id)
    obs = env.reset()
    
    action_schema = Action.model_json_schema()
    
    system_prompt = f"""You are a helpful SaaS Cloud API support agent. 
You are managing a tier-1 inbox. Your available actions are strictly JSON matching this schema:
{json.dumps(action_schema)}

Rules:
1. classify_ticket if the ticket category is obvious (Billing, Technical, Account, Other).
2. search_kb for technical facts before replying.
3. reply_ticket to solve the user's issue.
4. escalate_ticket if the request involves massive data loss, enterprise sales negotiation, or extreme anger.
5. close_ticket when the ticket is fully addressed. YOU MUST ACT (reply, escalate, classify) BEFORE CLOSING.
"""

    hf_token = os.environ.get("HF_TOKEN")
    from huggingface_hub import InferenceClient
    client = InferenceClient("meta-llama/Llama-3.3-70B-Instruct", token=hf_token)

    total_reward = 0.0
    step_count = 0

    while not env.done:
        step_count += 1
        print(f"\n[Obs | Queue: {obs.tickets_remaining} left]")
        if obs.current_ticket:
            print(f"Ticket: [{obs.current_ticket.ticket_id}] {obs.current_ticket.subject} (Priority: {obs.current_ticket.priority})")
        print(f"Last Status: {obs.last_action_status}")
            
        obs_dict = obs.model_dump()
        user_prompt = f"Current observation:\n{json.dumps(obs_dict, indent=2)}\nReturn your valid JSON Action."
        
        try:
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            response = client.chat_completion(
                messages=messages, max_tokens=250, response_format={"type": "json_object"}
            )
            action_json = response.choices[0].message.content

            action_data = json.loads(action_json)
            action = Action(**action_data)
        except Exception as e:
            print("Action Failed:", e)
            action = Action(action_type="close_ticket", ticket_id="fallback")
            
        print(f"-> Agent Action: {action.action_type}")
        obs, reward, done, info = env.step(action)
        total_reward += reward.score
        
        print(f"[STEP] step={step_count} reward={reward.score}", flush=True)
        
        if done:
            break
            
    score = evaluate_history(task_id, env.history)
    print(f"\nTask {task_id} completed | Final Score (0.0 - 1.0): {score:.2f} | Total Accumulated Reward: {total_reward:.2f}")
    print(f"[END] task={task_id} score={score} steps={step_count}", flush=True)
    return score

if __name__ == "__main__":
    total = 0
    for task_id in TASKS.keys():
        s = run_agent_on_task(task_id)
        total += s
    print(f"\n{'*'*50}")
    print(f"BASELINE RUN COMPLETE. Total Score: {total:.2f} / {len(TASKS)}. Average: {(total/len(TASKS)):.2f}")
    print(f"{'*'*50}\n")
