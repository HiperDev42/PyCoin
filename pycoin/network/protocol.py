from pydantic import BaseModel

class Message(BaseModel):
    magic: bytes
    command: str
    length: int
    checksum: bytes
    payload: dict
