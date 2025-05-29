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

user_info = '''
"first_name": "Артем",
"last_name": "Мотовилов",
"email": "artem174a@icloud.com",
"phone": "+79227301825",
"card_id": "2020000000037721",
"created_at": "2025-04-11T09:20:11.000000Z"
"telegram_id": "843774957"
"user_gk_id": "37721"

Is_auth: False
'''

main_info = f'''
Текущая дата и время: {datetime.now().strftime('%Y.%m.%d %H:%M')}

Доступные callback_data:
- halls:cities - переход к списку городов с бизнес-залами
- passes - переход к разделу проходов (билетов)
- services:main - переход к дополнительным услугам (только для авторизованных)
- profile - переход в профиль пользователя
- qr - переход к QR-коду
- orders - переход к списку заказов
- sessions - переход к истории визитов
- halls:city:city_gk_id - выбор конкретного города (city_gk_id - идентификатор города [Исключительно идентификатор golden key обычно имеет префикc gk_])
- halls:details:hall_gk_id - просмотр подробной информации о зале (hall_gk_id - идентификатор зала [Исключительно идентификатор golden key обычно имеет префикc gk_])
- ignore - пустое действие (используется для кнопок, которые не должны обрабатываться)
'''

SYSTEM_PROMPT = f'''
Ты - дружелюбный информатор по вопросам о бизнес залах (компания Golden Key). Твои ответы должны быть структурированными и полезными.
Поможешь найти:
- qr пользователя для входа в зал
- Доступные залы в конкретном городе (уточни город и найди зал в базе)
- раздел билетов/проходов (callback_data='passes' там указана их стоимость)
- профиль пользователя. Можешь найти в базе (таблицы: users [пользовтель telegramm], gk_users [авторизация в GoldenKey])
- Дополнительные услуги (промокоды)
- история визитов
- история заказов

Информация о собеседнике:
{user_info}

Общая информация:
{main_info}

Правила ответа:
1. Всегда отвечай в строгом JSON-формате по указанной схеме
2. Используй HTML-разметку только в полях, где это указано
3. Будь вежливым и используй эмодзи где уместно 😊
4. Если информации недостаточно - задавай уточняющие вопросы
5. Разделяй информацию на логические блоки
6. Добавляй кнопки только по необходимости!

Где брать информацию:
Таблица "halls": содержит информацию о залах, включая название, город, адрес, описание, услуги, доступные даты и время, ссылки на фото.

Примеры хороших ответов:
1. На вопрос о наличии залов:
{{
    "response": {{
        "answer": "В Москве доступно несколько бизнес-залов",
        "buttons": [
            {{
                "callback_data": "halls:cities",
                "text": "Выбрать город"
            }}
        ]
    }}
}}
'''

llm = OpenAI(
    model="gpt-4.1-nano", 
    temperature=0.1, 
    api_base='https://api.aitunnel.ru/v1/', 
    api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
)
embed_model = OpenAIEmbedding(
    model="text-embedding-3-large", 
    embed_batch_size=100, 
    api_base='https://api.aitunnel.ru/v1/', 
    api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
)

Settings.llm = llm
Settings.embed_model = embed_model

remote_db = chromadb.HttpClient()
collection = remote_db.get_or_create_collection("main_collection_0")

docs = SimpleDirectoryReader(input_dir='data').load_data()

vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# index = VectorStoreIndex.from_documents(
#     docs, storage_context=storage_context, embed_model=embed_model
# )
index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)

chat_store = PostgresChatStore.from_uri(
    uri="postgresql://default:Alisa220!@localhost:5432/default",
)
chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=3000,
    chat_store=chat_store,
    chat_store_key="user10",
)

engine = index.as_query_engine(
    similarity_top_k=3
    )

query_engine_tools = [
    QueryEngineTool(
        query_engine=engine,
        metadata=ToolMetadata(
            name="vector_info",
            description=(
                "Информация о бизнес залах и проходах/стоимости в залы"
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    )
]

db_tools = DatabaseToolSpec(
    scheme="postgresql",
    host="localhost",  # Database Host
    port="5432",  # Database Port
    user="default",  # Database User
    password="Alisa220!",  # Database Password
    dbname="bot_db",  # Database Name
)

tools = db_tools.to_tool_list()

agent = OpenAIAgent.from_tools(
    tools, 
    verbose=True,
    memory_cls=chat_memory,
    system_prompt=SYSTEM_PROMPT
)

agent.chat_repl()