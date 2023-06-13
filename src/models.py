from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    # These are both generated based on the hash
    # link = Column(String)
    # feed_url = Column(String)
    description = Column(String)
    subtitle = Column(String)
    feed_url = Column(String, unique=True, index=True)

    posts = relationship("Post", back_populates="owner")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    link = Column(String)
    content = Column(String)
    author = Column(String)
    publication_date = Column(Integer)
    update_date = Column(Integer, default=lambda: int(datetime.utcnow().timestamp()))
    owner_id = Column(Integer, ForeignKey("feeds.id"))

    owner = relationship("Feed", back_populates="posts")
