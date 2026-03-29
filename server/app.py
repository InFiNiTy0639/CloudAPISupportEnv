import uvicorn
from fastapi import FastAPI, Body, Request
from pydantic import BaseModel
from typing import Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from env import CustomerSupportEnv
from models import Action

app = FastAPI()

current_env = None

@app.post("/reset")
async def reset(request: Request):
    global current_env
    try:
        data = await request.json()
        task_id = data.get("task_id", "easy_classify")
    except Exception:
        task_id = "easy_classify"
        
    current_env = CustomerSupportEnv(task_id)
    obs = current_env.reset()
    return obs.model_dump()

@app.post("/step")
def step(action: Action):
    global current_env
    if current_env is None:
        current_env = CustomerSupportEnv("easy_classify")
        current_env.reset()
    
    obs, reward, done, info = current_env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info
    }

@app.get("/state")
def state():
    global current_env
    if current_env is None:
        return {"error": "Environment not initialized"}
    return current_env.state().model_dump()

@app.get("/")
def read_root():
    return {"message": "Cloud API Support OpenEnv Multi-mode Server is running", "status": "Ready"}

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
