from pydantic import BaseModel, Field

from doitall.knowledge.document import Document
from doitall.models.memory import Memory
from doitall.models.message import Message


class RuntimeContext(BaseModel):
    messages: list[Message] = Field(default_factory=list)
    memories: list[Memory] = Field(default_factory=list)
    knowledge: list[Document] = Field(default_factory=list)
