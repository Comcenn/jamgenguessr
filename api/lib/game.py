from enum import Enum
from json import dumps, loads
from random import choice
from typing import Dict, List, Optional, Protocol
from logging import getLogger

from fastapi import WebSocket

from api.lib.player import Player


LOGGER = getLogger("uvicorn")


class Manager(Protocol):

    async def broadcast_to_game(game_id: str, message: str) -> None:
        ...


class MessageTypes(str, Enum):
    JOINED = "JOINED"
    CONFIG = "CONFIG"
    GENERATED = "GENERATED"
    GUESS = "GUESS"
    NEW_ROUND = "NEW_ROUND"


class Game:
    def __init__(self, id: str, mngr: Manager, player: Optional[Player] = None) -> None:
        self.id = id
        self.mngr = mngr
        self.creator = player
        self.players: Dict[str: Player] = {}
        self.round = 0
        self.controller = player.id
        self.image_url = ""
        self.prompt = ""
        self.guesses = set()
    
    async def init(self) -> None:
        LOGGER.info(f"Adding creator {self.creator.id}")
        await self.add_player(self.creator)
    
    async def add_player(self, player: Player) -> None:
        if player.id in self.players:
            self.players[player.id].websocket = player.websocket
            return
        else:
            self.players[player.id] = player
        LOGGER.info("Broadcasting....")
        await self.mngr.broadcast_to_game(
                    self.id,
                    dumps({
                        "type": MessageTypes.CONFIG,
                        "playerId": player.id,
                        "target": player.id,
                        "nextScore": player.score,
                        "roundNumber": self.round,
                        "controllerId": self.controller,
                        "imageUrl": self.image_url
            })
            )
    
    def finish_round(self, player_id: str) -> Dict[str, any]:
        self.round += 1
        self.prompt = ""
        self.image_url = ""
        self.guesses = set()
        self.controller = choice([player.id for player in self.players.values()])
        return {
                "type": MessageTypes.NEW_ROUND,
                "playerId": "MNGR",
                "gameId": self.id,
                "controllerId": self.controller,
                "roundNumber": self.round,
                "nextScore": self.players[player_id].score,
                "scores": [{"playerId": player.id, "playerScore": player.score} for player in self.players.values()]
                }
    
    async def update_game(self, message: Dict[str, any] ) -> None:
        LOGGER.info(f"Update_game: {message}")
        LOGGER.info(f"Guesses: {self.guesses}, Players: {self.players}, Players minus Controller: {set(player for player in self.players.keys() if player != self.controller)}")
        data = loads(message["data"].decode("utf-8"))
        player_id = data["playerId"]
        msg = None
        if (msg_type := data["type"]) == MessageTypes.JOINED and player_id not in self.players:
            self.players[player_id] = Player(id=player_id)
        elif msg_type == MessageTypes.GENERATED:
            self.image_url = data["imageUrl"]
            self.prompt = data["prompt"]
        elif len(self.players) < 2:
            return
        elif msg_type == MessageTypes.GUESS:
            if player_id not in self.guesses:
                self.guesses.add(player_id)
                if data["prompt"] == self.prompt:
                    self.players[player_id].score += 1
                    msg = self.finish_round(player_id)
                
        if msg:    
            await self.mngr.broadcast_to_game(self.id, dumps(msg))
        
        if len(self.players) >= 2 and self.guesses == set(player for player in self.players.keys() if player != self.controller):
            msg = self.finish_round(player_id)
            await self.mngr.broadcast_to_game(self.id, dumps(msg))
        
    
    @property
    def sockets(self) -> List[WebSocket]:
        return [player.websocket for player in self.players.values() if player.websocket]