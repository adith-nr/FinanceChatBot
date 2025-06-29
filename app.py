from fastapi import FastAPI
from pydantic import BaseModel
from finance_agent import run_finance_agent
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

import json
class Prompt(BaseModel):
    prompt:str
    context:List[Dict[str, str]]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.post('/')
def start(prompt:Prompt):
    
    print(prompt.context)
    result = run_finance_agent(prompt.prompt,prompt.context)
    
    return {"response": result}