from llama_index.core import Document
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.agent.openai import OpenAIAgent
from llama_index.storage.chat_store.postgres import PostgresChatStore
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.tools.database import DatabaseToolSpec
import chromadb
from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

class GoldenKeyAgent:
    def __init__(self):
        # Инициализация настроек и подключений
        self.llm = OpenAI(
            model="gpt-4.1-nano", 
            temperature=0.1, 
            api_base='https://api.aitunnel.ru/v1/', 
            api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
        )
        self.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large", 
            embed_batch_size=100, 
            api_base='https://api.aitunnel.ru/v1/', 
            api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
        )

        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        # Инициализация ChromaDB
        self.remote_db = chromadb.HttpClient()
        self.collection = self.remote_db.get_or_create_collection("main_collection_0")

        # Загрузка документов и создание индекса
        # docs = SimpleDirectoryReader(input_dir='data').load_data()
        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        # storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.index = VectorStoreIndex.from_vector_store(vector_store, embed_model=self.embed_model)

        # Инициализация движка запросов
        self.engine = self.index.as_query_engine(similarity_top_k=3)

        # Создание инструментов для агента
        query_engine_tools = [
            QueryEngineTool(
                query_engine=self.engine,
                metadata=ToolMetadata(
                    name="vector_info",
                    description=(
                        "Информация о бизнес залах и проходах/стоимости в залы"
                        "Use a detailed plain text question as input to the tool."
                    ),
                ),
            )
        ]

        # Инициализация инструментов базы данных
        self.db_tools = DatabaseToolSpec(
            scheme="postgresql",
            host="localhost",
            port="5432",
            user="default",
            password="Alisa220!",
            dbname="bot_db",
        )

        # Объединение всех инструментов
        self.tools = self.db_tools.to_tool_list()

    def get_system_prompt(self, user_info: dict) -> str:
        """Генерация системного промпта с информацией о пользователе и текущем времени"""
        with open('system_prompt.md', 'r') as file:
            system_prompt = file.read()
        return system_prompt.replace('--user_info--', user_info)

    def ask_question(self, question: str, user_info: dict, chat_id: str) -> str:
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
        chat_store = PostgresChatStore.from_uri(
            uri="postgresql://default:Alisa220!@localhost:5432/default",
        )
        chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=chat_store,
            chat_store_key=chat_id,
        )

        # Создание агента с текущими настройками
        agent = OpenAIAgent.from_tools(
            self.tools, 
            memory_cls=chat_memory,
            system_prompt=self.get_system_prompt(user_info)
        )
        
        # Получение ответа от агента
        response = agent.chat(question)
        
        return str(response)