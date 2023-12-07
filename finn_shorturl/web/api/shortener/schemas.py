from pydantic import AnyHttpUrl, BaseModel


class ShortURLInput(BaseModel):
    url: AnyHttpUrl


class ShortUrlOutput(BaseModel):
    url: AnyHttpUrl
    short: AnyHttpUrl
