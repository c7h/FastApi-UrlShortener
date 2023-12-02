from pydantic import AnyHttpUrl, BaseModel, constr
from finn_shorturl.settings import shorturl_regex

class ShortURLInput(BaseModel):
    longurl: AnyHttpUrl


class ShortUrlOutput(BaseModel):
    shorturl: constr(regex=shorturl_regex, to_lower=True, strip_whitespace=True)