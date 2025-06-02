# from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.prompts import BasePromptTemplate, PromptTemplate
from llama_index.core import Settings
from llama_index.agent.openai import OpenAIAgent
from llama_index.storage.chat_store.postgres import PostgresChatStore
from llama_index.storage.chat_store.redis import RedisChatStore
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.tools.database import DatabaseToolSpec
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.prompts import RichPromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
import json
from pydantic import BaseModel
from textwrap import dedent
from openai import OpenAI

from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine, DEFAULT_RESPONSE_SYNTHESIS_PROMPT_V2
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
    
)
from llama_index.core import VectorStoreIndex

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_redis import RedisChatMessageHistory

class Result(BaseModel):
            class Button(BaseModel):
                callback_data: str
                text: str

            answer: str
            buttons: list[Button]

class GoldenKeyAgent:
    def __init__(self):
        # Инициализация настроек и подключений
        pass
        # self.llm = OpenAI(
        #     model="gpt-4.1-nano", 
        #     temperature=0.8, 
        #     api_base='https://api.aitunnel.ru/v1/', 
        #     api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
        # )
        # self.embed_model = OpenAIEmbedding(
        #     model="text-embedding-3-large", 
        #     embed_batch_size=600,
        #     api_base='https://api.aitunnel.ru/v1/', 
        #     api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
        # )

        # Settings.llm = self.llm
        # Settings.embed_model = self.embed_model


    def get_system_prompt(self, user_info: dict) -> str:
        """Генерация системного промпта с информацией о пользователе и текущем времени"""
        with open('system_prompt.md', 'r') as file:
            system_prompt = file.read()
        return system_prompt.replace('--user_info--', user_info)

    def ask_question(self, question: str, user_info: dict, chat_id: str) -> Result:
        """
        Задает вопрос агенту и возвращает ответ
        
        Args:
            question: Вопрос пользователя
            user_info: Словарь с информацией о пользователе
            chat_id: Идентификатор чата для хранения истории
            
        Returns:
            Ответ агента в виде строки
        """
        # Инициализация хранилища чата и памяти
        system_prompt = self.get_system_prompt(user_info)

        client = OpenAI(
            api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI',
            base_url="https://api.aitunnel.ru/v1/"
        )

        MODEL = "gpt-4.1-nano"

        completion = client.beta.chat.completions.parse(
                    temperature=0.8,
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    response_format=Result
                )
                
        response = completion.choices[0].message
        return response.parsed



     