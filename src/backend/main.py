from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import warnings
warnings.filterwarnings("ignore")

from src.backend.agents.orchestrator import Orchestrator, OrchestratorState
from src.backend.tools import save_newsletter

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Welcome to AI Nexus Herald!"}

@app.post("/generate")
async def generate_newsletter():
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        orchestrator = Orchestrator(groq_api_key)
        graph = orchestrator.build_orchestrator_graph()

        initial_state = OrchestratorState()
        
        try:
            final_state = graph.invoke(initial_state) 
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise e
        
        newsletter = final_state["newsletter"]

        # Save the newsletter
        save_newsletter(newsletter)

        return QueryResponse(response=newsletter.content)
    except Exception as e:
        return QueryResponse(response=f"Error occurred: {str(e)}")