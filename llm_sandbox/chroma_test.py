from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent.workflow import FunctionAgent
import chromadb

llm = OpenAI(
    model="gpt-4.1-nano", 
    temperature=0.1, 
    api_base='https://api.aitunnel.ru/v1/', 
    api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
)
embed_model = OpenAIEmbedding(
    model="text-embedding-3-small", 
    embed_batch_size=100, 
    api_base='https://api.aitunnel.ru/v1/', 
    api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI'
)

Settings.llm = llm
Settings.embed_model = embed_model

remote_db = chromadb.HttpClient()
halls_collection = remote_db.get_or_create_collection("halls_collection")
products_collection = remote_db.get_or_create_collection("products_collection")

documents = SimpleDirectoryReader("data").load_data()

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, embed_model=embed_model
)
# index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
query_engine = index.as_query_engine()



# list_tool = QueryEngineTool.from_defaults(
#     query_engine=data_query_engine,
#     description="Полезный инструмент для получения информации о техническом задании",
# )

# query_engine = RouterQueryEngine(
#     selector=PydanticSingleSelector.from_defaults(),
#     query_engine_tools=[
#         list_tool,
#     ],
#     verbose=True,
# )

# response = query_engine.query("Сколько стоит визит?")
# print(response)