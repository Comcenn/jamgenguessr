from asyncio import create_task
from json import dumps
from typing import Dict
from uuid import UUID

from fastapi import WebSocket
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from api.lib.game import Game
from api.lib.player import Player, Roles
from api.lib.redis import RedisClient


class GameManager:

    def __init__(self) -> None:
        self.games: Dict[str: Game] = {}
        self.store_client = RedisClient()
    
    async def add_player_to_game(self, game_id: str, player: Player) -> None:
        await player.websocket.accept()

        if not hasattr(self.store_client, "connection"):
            await self.store_client.connect()

        if game_id in self.games or game_id in await self.store_client.connection.pubsub_channels():
            await self.games[game_id].add_player(player)
        else:
            player.role = Roles.CONTROLLER
            game = Game(game_id, self, player)
            self.games[game_id] = game
            subscription = await self.store_client.subscribe(game_id)
            create_task(self._data_store_data_reader(subscription))

            await game.init()
            

    
    async def broadcast_to_game(self, game_id: str, message: str) -> None:
        await self.store_client.publish(game_id, message)
    
    async def remove_player_from_game(self, game_id:str, player_id: UUID) -> None:
        self.games[game_id].players.pop(player_id)
        if len(self.games) == 0:
            del self.games[game_id]
            await self.store_client.unsubscribe(game_id)
    
    async def _data_store_data_reader(self, subscription: PubSub) -> None:
        while True:
            message = await subscription.get_message(ignore_subscribe_messages=True)
            if message is not None:
                game_id = message["channel"].decode("utf-8")
                game: Game = self.games[game_id]
                await game.update_game(message)
                for socket in game.sockets:
                    data = message["data"].decode("utf-8")
                    await socket.send_text(data)