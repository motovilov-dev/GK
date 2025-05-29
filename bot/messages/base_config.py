from pydantic import BaseModel
from typing import Dict, Type

class BaseMessageModel(BaseModel):
    # Общие сообщения, которые есть на всех языках
    start: str
    help: str
    unknown_command: str
    
    def get_start_message(self, first_name: str) -> str:
        return self.start.format(first_name=first_name)