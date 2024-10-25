from datetime import datetime

from pydantic import BaseModel, validator

from metadata import SITE_URL


class PostBase(BaseModel):
    title: str = ""
    description: str = ""
    link: str = ""
    content: str = ""
    author: str = ""
    publication_date: int = 0


class PostNew(PostBase):
    secret: str

    @validator("content")
    def url_or_body(cls, v, values):
        link = values.get("link", "")
        if not v and not link:
            raise ValueError("Must supply at least a link (url) or content")
        return v

    @validator("publication_date", always=True)
    def pdate(cls, v):
        if not v:
            v = int(datetime.utcnow().timestamp())
        return v


class Post(PostBase):
    id: int
    owner_id: int
    update_date: int

    class Config:
        orm_mode = True


class FeedBase(BaseModel):
    title: str
    description: str = ""
    subtitle: str = ""


class FeedNew(FeedBase):
    secret: str


class Feed(FeedBase):
    id: int
    feed_url: str
    posts: list[Post] = []

    @validator("feed_url")
    def url_validate(cls, v):
        return f"{SITE_URL}/feeds/{v}.atom.xml"

    class Config:
        orm_mode = True
