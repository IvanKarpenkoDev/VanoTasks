# """Пример работы с чатом через gigachain"""
# from fastapi import APIRouter
# from langchain.schema import HumanMessage, SystemMessage
# from langchain.chat_models.gigachat import GigaChat
#
# router = APIRouter(
#     prefix="/gigachat",
#     tags=["GigaChat"]
# )
#
# chat = GigaChat(
#     credentials='ZGNhZmExYWYtM2M5ZC00YTI2LWIzZmYtYjIyYTU1OTJiZTg4OmI0ZmEzY2Y5LTg5ZTItNGUxYi04YWNjLTBiZjkxMDY1YmU5Zg==',
#     verify_ssl_certs=False)
#
# messages = [
#     SystemMessage(
#         content="Ты эмпатичный бот-психолог, который помогает пользователю решить его проблемы."
#     )
# ]
#
#
# @router.post("/answer/")
# async def get_answer(question: str):
#
#     return {"answer": }
#
#
# while(True):
#     user_input = input("User: ")
#     messages.append(HumanMessage(content=user_input))
#     res = chat(messages)
#     messages.append(res)
#     print("Bot: ", res.content)
