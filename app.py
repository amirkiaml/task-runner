from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timezone

from orchestrator import run_task
from storage import save_task, list_tasks, clear_all_tasks

app = FastAPI()


class AgentRequest(BaseModel):
    user_input: str


@app.get("/")
async def home():
    return FileResponse("static/index.html")


@app.post("/run")
async def run_agent(request: AgentRequest):
    try:
        result = run_task(request.user_input)
    except Exception as e:
        return {"error": f"Task processing failed: {e}"}

    timestamp = datetime.now(timezone.utc).isoformat()
    task_id = save_task(request.user_input, result["final_output"], result["tools_used"], result["trace"])

    return {
        "id": task_id,
        "response": result["final_output"],
        "tools_used": result["tools_used"],
        "trace": result["trace"],
        "timestamp": timestamp,
    }


@app.get("/history")
async def get_history():
    return list_tasks()


@app.delete("/history")
async def delete_history():
    clear_all_tasks()
    return {"status": "cleared"}


app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, ws="none")
