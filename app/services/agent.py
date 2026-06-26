from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session
from app.config import settings
from app.db import crud
import time


class ChefAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
            api_key=settings.GROQ_API_KEY
        )

        self.system_prompt = """
        You are an expert chef assistant who knows
        recipes from all cuisines especially Indian.

        When user asks for a recipe provide:
        🥘 Dish Name
        🛒 Ingredients with quantities
        👨‍🍳 Step by step procedure
        ⏱️ Cooking time
        ⭐ Difficulty level
        💡 Pro tips

        {user_context}

        Be friendly and encouraging!
        Remember previous recipe context.
        Respond in same language as user.
        """

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

        self.chain = self.prompt | self.llm | StrOutputParser()

        self.title_prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a short descriptive phrase summarizing the user's message, like a conversation title (e.g., 'DSA and Python problem solving', 'Free Claude code installation guide'). Do not use quotes or punctuation. Keep it under 6 words."),
            ("human", "{input}")
        ])
        self.title_chain = self.title_prompt | self.llm | StrOutputParser()

    def generate_and_save_title(self, db: Session, session_id: str, message: str):
        try:
            title = self.title_chain.invoke({"input": message}).strip('" \n')
            crud.update_session_title(db, session_id, title)
        except Exception as e:
            print("Title generation error:", e)

    def chat(self, db: Session, message: str, session_id: str, user_id: int = None, username: str = None) -> str:
        crud.get_or_create_session(db, session_id, user_id=user_id)
        chat_history = crud.get_chat_history(db, session_id, settings.MAX_HISTORY)

        if not chat_history:
            self.generate_and_save_title(db, session_id, message)

        user_context = f"The user you are talking to is named '{username}'. Address them by their name occasionally and remember it." if username else ""

        response = self.chain.invoke({
            "input": message,
            "chat_history": chat_history,
            "user_context": user_context
        })

        crud.save_message(db, session_id, "human", message)
        crud.save_message(db, session_id, "ai", response)

        return response

    def chat_stream(self, db: Session, message: str, session_id: str, user_id: int = None, username: str = None):
        crud.get_or_create_session(db, session_id, user_id=user_id)
        chat_history = crud.get_chat_history(db, session_id, settings.MAX_HISTORY)

        if not chat_history:
            self.generate_and_save_title(db, session_id, message)

        crud.save_message(db, session_id, "human", message)

        user_context = f"The user you are talking to is named '{username}'. Address them by their name occasionally and remember it." if username else ""

        full_response = ""

        for chunk in self.chain.stream({
            "input": message,
            "chat_history": chat_history,
            "user_context": user_context
        }):
            full_response += chunk
            yield chunk
            time.sleep(0.02)

        crud.save_message(db, session_id, "ai", full_response)


chef_agent = ChefAgent()