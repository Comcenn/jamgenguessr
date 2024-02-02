
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from fastapi import WebSocket


class Roles(str, Enum):
    CONTROLLER = "CONTROLLER"
    GUESSER = "GUESSER"


@dataclass
class Player:
    role: Roles
    websocket: Optional[WebSocket]
    id: str = str(uuid4())
    score: int = 0