from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from graph.workflow import app

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    file_path: str | None = None


@router.post("/ask")
async def ask(request: AskRequest):

    print("=" * 50)
    print("Question :", request.question)
    print("File Path:", request.file_path)
    print("=" * 50)

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=request.question)
            ],
            "file_path": request.file_path,
        }
    )

    print(result)

    messages = result["messages"]

    final_answer = messages[-1].content

    return {
        "final_answer": final_answer
    }