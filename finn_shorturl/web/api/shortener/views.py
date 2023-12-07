from typing import Annotated
from fastapi import APIRouter, responses, Request, Path, HTTPException, Depends
from .schemas import ShortUrlOutput, ShortURLInput
from finn_shorturl.services.redis.dependency import get_redis_pool
from finn_shorturl.settings import settings
from redis.asyncio import ConnectionPool, Redis
import random

router = APIRouter()


@router.get("/{shorturl_id}", include_in_schema=False)
async def forward(
    shorturl_id: str,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
):
    """
    This is the resource itself. For convenience reasons, this is used to
    forward from the shortened URL to the target URL
    """
    async with Redis(connection_pool=redis_pool) as redis:
        db_result = await redis.get(shorturl_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="URL not found")
    url = db_result.decode()

    return responses.RedirectResponse(url)


@router.get("/decode/{shorturl_id}", response_model=ShortUrlOutput)
async def decode_url(
    req: Request,
    shorturl_id: Annotated[
        str, Path(title="The ID part of the shortened URL", example="AbC12XyZ")
    ],
    redis_pool: ConnectionPool = Depends(get_redis_pool),
):
    # Lookup shorturl_id in DB
    async with Redis(connection_pool=redis_pool) as redis:
        db_result = await redis.get(shorturl_id)
    # throw 404 if not found in DB
    if not db_result:
        raise HTTPException(status_code=404, detail="URL not found")
    url = db_result.decode()

    shorturl = str(req.base_url).rstrip("/") + router.url_path_for(
        "forward", shorturl_id=shorturl_id
    )
    return ShortUrlOutput(url=url, short=shorturl)


@router.post("/encode", response_model=ShortUrlOutput)
async def encode_url(
    req: Request,
    item: ShortURLInput,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
) -> None:
    """
    Creates a new shorturl and stores it (if valid)
    """

    # create new shourturl id
    def _create_shorturl_id():
        shorturl_id = "".join(
            random.choice(settings.shorturl_characters) for _ in range(8)
        )
        return shorturl_id

    # create new entry in DB async
    while True:
        shorturl_id = _create_shorturl_id()
        async with Redis(connection_pool=redis_pool) as redis:
            res = await redis.setnx(shorturl_id, str(item.url))
            if res == True:
                # ID was unique. no reason to try again...
                break

    shorturl = str(req.base_url).rstrip("/") + router.url_path_for(
        "forward", shorturl_id=shorturl_id
    )
    return ShortUrlOutput(url=item.url, short=shorturl)
