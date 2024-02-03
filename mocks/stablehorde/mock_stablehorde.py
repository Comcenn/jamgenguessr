from logging import getLogger
from os import environ
from typing import Dict, List, Union
from uuid import uuid4
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel


LOGGER = getLogger("uvicorn")


class GenerateAsyncRequestParams(BaseModel):
    sampler_name: str
    cfg_scale: float
    denoising_strength: float
    seed: str
    height: int
    width: int
    seed_variation: int
    post_processing: List[str]
    karras: bool
    tiling: bool
    hires_fix: bool
    clip_skip: int
    steps: int
    n: int


class GenerateAsyncRequest(BaseModel):
    params: GenerateAsyncRequestParams 
    nsfw: bool
    censor_nsfw: bool
    disable_batching: bool


class GenerateAsyncResponse(BaseModel):
    id: str


class Generation(BaseModel):
    img: str


class GenerateStatusResponse(BaseModel):
    faulted: bool
    finished: bool
    generations: List[Generation]
    processing: bool
    waiting: bool 


app = FastAPI()


@app.post("/generate/async", response_model=GenerateAsyncResponse)
async def get_image_id(request: GenerateAsyncRequest) -> Dict[str, str]:
    LOGGER.info(f"Request: {request}")
    return {"id": str(uuid4())}


@app.get("/generate/status/{image_id}", response_model=GenerateStatusResponse)
async def get_image(image_id: str) -> Dict[str, Union[bool, List[Dict[str, str]]]]:
    image_url = "http://127.0.0.1:5000/file"  
    LOGGER.info(f"Image ID: {image_id}, Image URL: {image_url}")
    return {
        "faulted": False,
        "finished": True,
        "generations": [{"img": image_url}],
        "processing": False,
        "waiting": False
    }


@app.get("/file", response_class=FileResponse)
async def get_file() -> str:
    image_url = environ.get("MOCK_IMAGE_URL")
    return image_url