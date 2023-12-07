import random
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, responses
from redis.asyncio import ConnectionPool, Redis

from finn_shorturl.services.redis.dependency import get_redis_pool
from finn_shorturl.settings import settings

from .schemas import ShortURLInput, ShortUrlOutput

router = APIRouter()


async def lookup_url(shorturl_id, redis_pool):
    async with Redis(connection_pool=redis_pool) as redis:
        db_result = await redis.get(shorturl_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="URL not found")
    url = db_result.decode()
    return url


def get_absolute_shorturl(shorturl_id: str, req: Request):
    base = str(req.base_url)
    lookup_endpoint = router.url_path_for("forward", shorturl_id=shorturl_id)
    shorturl = f"{base.rstrip('/')}/api{lookup_endpoint}"
    return shorturl


@router.get("/{shorturl_id}", include_in_schema=False)
async def forward(
    shorturl_id: str,
    redis_pool: ConnectionPool = Depends(get_redis_pool),
):
    """
    This is the resource itself. For convenience reasons, this is used to
    forward from the shortened URL to the target URL
    """
    url = await lookup_url(shorturl_id, redis_pool)

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
    url = await lookup_url(shorturl_id, redis_pool)

    shorturl = get_absolute_shorturl(shorturl_id, req)
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

    shorturl = get_absolute_shorturl(shorturl_id, req)

    return ShortUrlOutput(url=item.url, short=shorturl)
