from fastapi import APIRouter
from .schemas import ShortUrlOutput

router = APIRouter()

@router.post("/encode")
def encode_url() -> None:
    """
    Creates a new shorturl and stores it (if valid)
    """
    pass


@router.get('/decode/{shourturl_id}', response_model=ShortUrlOutput)
async def decode_url(shorturl: Mapping = Depends(valid_shourturl_id)):
    return url