from json import dumps
import random
import string

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from api.lib.game_manager import GameManager
from api.lib.player import Player, Roles

from api.schema import game as Game


game_manager = GameManager()

router = APIRouter(
    prefix="/game",
    tags=["game"],
    responses={404: {"description": "Not found"}},
)


@router.get("/new", response_model=Game.NewGame)
async def new_game():
    game_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    return RedirectResponse(f"http://localhost:3000/game?id={game_id}")


@router.websocket("/join/{game_id}/{player_id}")
async def join_game(game_id: str, player_id, websocket: WebSocket) -> None:
    player = Player(id=player_id, role=Roles.GUESSER, websocket=websocket)
    await game_manager.add_player_to_game(game_id, player)
    message = {
        "playerId": player.id,
        "type": "JOINED",
        "gameId": game_id,
        "message": f"PLayer {player.id} connected to game - {game_id}"
    }
    await game_manager.broadcast_to_game(game_id, dumps(message))
    try:
        while True:
            data = await websocket.receive_text()
            await game_manager.broadcast_to_game(game_id, data)
    except WebSocketDisconnect:
        await game_manager.remove_player_from_game(game_id, player.id)
        message = {
            "playerId": player.id,
            "type": "DISCONNECTED",
            "gameId": game_id,
            "message": f"Player {player.id} disconnected from room - {game_id}"
        }
        await game_manager.broadcast_to_game(game_id, dumps(message))
