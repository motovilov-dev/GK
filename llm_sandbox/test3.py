import sqlite3
from typing import List, Dict, Any, Optional
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain.chat_models import ChatOpenAI  # Или другой совместимый LLM
from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
import requests


class GPTNanoSQLAssistant:
    """
    Класс для взаимодействия с GPT-4.1-nano через SQL базу данных.
    Позволяет задавать вопросы на естественном языке и получать ответы на основе данных в БД.

    Аргументы:
        db_uri (str): URI для подключения к SQL базе данных
        llm_model (str): Название модели LLM (по умолчанию 'gpt-4')
        temperature (float): Параметр температуры для модели (по умолчанию 0)
        verbose (bool): Режим отладки (по умолчанию False)
    """

    def __init__(
            self,
            db_uri: str = "sqlite:///:memory:",
            llm_model: str = "gpt-4.1-nano",
            temperature: float = 0,
            verbose: bool = False
    ):
        self.db_uri = db_uri
        self.llm_model = llm_model
        self.temperature = temperature
        self.verbose = verbose

        # Инициализация подключения к БД
        self.db = self._init_db()

        # Инициализация языковой модели
        self.llm = ChatOpenAI(
            model=self.llm_model,
            temperature=self.temperature,
            openai_api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI',
            openai_api_base='https://api.aitunnel.ru/v1/'
        )

        # Инициализация инструментов для работы с SQL
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

        # Создание агента для выполнения запросов
        self.agent_executor = self._create_agent()

    def _init_db(self) -> SQLDatabase:
        """
        Инициализирует подключение к SQL базе данных.

        Возвращает:
            SQLDatabase: Объект для работы с SQL базой данных
        """
        if self.db_uri == "sqlite:///:memory:":
            # Для демонстрации используем in-memory базу Chinook
            return self._init_chinook_db()
        else:
            # Подключение к пользовательской базе данных
            engine = create_engine(self.db_uri)
            return SQLDatabase(engine)

    def _init_chinook_db(self) -> SQLDatabase:
        """
        Инициализирует демонстрационную базу данных Chinook в памяти.

        Возвращает:
            SQLDatabase: Объект для работы с SQL базой данных Chinook
        """
        # Загрузка скрипта создания базы данных Chinook
        url = "https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql"
        response = requests.get(url)
        sql_script = response.text

        # Создание in-memory SQLite базы
        connection = sqlite3.connect(":memory:", check_same_thread=False)
        connection.executescript(sql_script)

        # Создание SQLAlchemy engine
        engine = create_engine(
            "sqlite://",
            creator=lambda: connection,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )

        return SQLDatabase(engine)

    def _create_agent(self) -> AgentExecutor:
        """
        Создает и настраивает агента для выполнения SQL запросов.

        Возвращает:
            AgentExecutor: Агент для выполнения запросов к базе данных
        """
        # Память для хранения контекста разговора
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Создание агента
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            tools=self.toolkit.get_tools(),
            llm=self.llm,
            verbose=self.verbose,
            memory=memory,
            handle_parsing_errors=True
        )

        return agent_executor

    def query(self, question: str) -> str:
        """
        Выполняет запрос к базе данных на естественном языке.

        Аргументы:
            question (str): Вопрос на естественном языке

        Возвращает:
            str: Ответ на основе данных из базы данных
        """
        try:
            result = self.agent_executor.run(question)
            return result
        except Exception as e:
            return f"Произошла ошибка при выполнении запроса: {str(e)}"

    def get_table_names(self) -> List[str]:
        """
        Возвращает список таблиц в базе данных.

        Возвращает:
            List[str]: Список имен таблиц
        """
        return self.db.get_usable_table_names()

    def get_table_schema(self, table_name: str) -> str:
        """
        Возвращает схему указанной таблицы.

        Аргументы:
            table_name (str): Имя таблицы

        Возвращает:
            str: Схема таблицы в SQL формате
        """
        return self.db.get_table_info([table_name])

    def execute_sql(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Выполняет SQL запрос напрямую и возвращает результат.

        Аргументы:
            sql_query (str): SQL запрос для выполнения

        Возвращает:
            List[Dict[str, Any]]: Результаты запроса в виде списка словарей
        """
        try:
            result = self.db.run(sql_query)
            return result
        except Exception as e:
            return [{"error": str(e)}]


# Пример использования
if __name__ == "__main__":
    # Инициализация ассистента с демонстрационной базой данных Chinook
    assistant = GPTNanoSQLAssistant(verbose=True)

    # Получение списка таблиц
    print("Доступные таблицы:", assistant.get_table_names())

    # Пример запроса на естественном языке
    question = "Какие 5 клиентов сделали самые большие покупки?"
    answer = assistant.query(question)
    print(f"Вопрос: {question}")
    print(f"Ответ: {answer}")

    # Пример прямого SQL запроса
    sql = "SELECT FirstName, LastName FROM Customer LIMIT 3"
    print(f"\nРезультат SQL запроса '{sql}':")
    print(assistant.execute_sql(sql))