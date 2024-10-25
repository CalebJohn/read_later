import hashlib
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

import models, schemas

FEED_MAX_SIZE = 1e9  # 1 GB
FEED_POST_LIFETIME_S = 60 * 60 * 24 * 90  # seconds


def hash_secret(secret: str) -> str:
    m = hashlib.sha256(bytes(secret, "utf-8"))
    return m.hexdigest()


def get_feed(db: Session, feed_id: int):
    return db.query(models.Feed).filter(models.Feed.id == feed_id).first()


def get_feed_by_hash(db: Session, hash: str):
    return db.query(models.Feed).filter(models.Feed.feed_url == hash).first()


def get_feed_by_secret(db: Session, secret: str):
    return get_feed_by_hash(db, hash_secret(secret))


def get_feed_size(db: Session, feed_id: int):
    """
    Used to place limits on the database size.
    For now feed size is defined as the byte size of the posts content column
    """
    size = (
        db.query(func.sum(func.length(models.Post.content)))
        .filter(models.Post.owner_id == feed_id)
        .first()
    )
    if size is None:
        raise Exception("Cannote read feed in order to enforce limits. Uh oh!")
    return size[0]


def create_feed(db: Session, feed: schemas.FeedNew):
    # 256 is more secure, but it's output is loooonngg
    hashed_secret = hash_secret(feed.secret)
    db_feed = models.Feed(
        title=feed.title,
        description=feed.description,
        subtitle=feed.subtitle,
        feed_url=hashed_secret,
    )
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    return db_feed


def create_empty_feed(db: Session, post: schemas.PostNew):
    new_feed = schemas.FeedNew(title="", secret=post.secret)
    return create_feed(db, new_feed)


def create_post(db: Session, post: schemas.PostNew, feed_id: int):
    new_post = post.dict()
    del new_post["secret"]
    db_post = models.Post(**new_post, owner_id=feed_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post_by_id(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def delete_oldest_post(db: Session, feed_id: int):
    oldest = (
        db.query(models.Post)
        .filter(models.Post.owner_id == feed_id)
        .order_by(models.Post.update_date.asc())
        .first()
    )
    if oldest is not None:
        db.delete(oldest)
    db.commit()


def enforce_storage_limits(db: Session, feed: schemas.Feed):
    # Ugly, but get's the job done
    size = get_feed_size(db, feed.id)
    while size is not None and size > FEED_MAX_SIZE:
        delete_oldest_post(db, feed.id)
        size = get_feed_size(db, feed.id)
    clear_old_posts(db)


def clear_old_posts(db: Session):
    now = datetime.utcnow().timestamp()
    filter_date = now - FEED_POST_LIFETIME_S
    db.query(models.Post).filter(models.Post.update_date <= filter_date).delete()
    db.commit()
