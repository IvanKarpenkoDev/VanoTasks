from fastapi import APIRouter
from langchain.schema import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

router = APIRouter(
    prefix="/gigachat",
    tags=["gigachat"]
)

chat = GigaChat(
    credentials='ZGNhZmExYWYtM2M5ZC00YTI2LWIzZmYtYjIyYTU1OTJiZTg4OmY5MzAzZjA5LTk0YzMtNGE2MS1hZGIxLTI1YzZkMzYxYTc3OA==',
    verify_ssl_certs=False)

messages = [
    SystemMessage(
        content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы."
    )
]


@router.post("/answer/")
async def get_answer(question):
    user_input = question
    messages.append(HumanMessage(content=user_input))
    res = chat(messages)
    messages.append(res)
    return {"answer": res.content}
