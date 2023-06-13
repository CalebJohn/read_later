import datetime

from feedgenerator import Atom1Feed, Rss201rev2Feed
from markupsafe import Markup

from . import schemas
from .metadata import SITE_URL


def _create_feed(feed: schemas.Feed, feed_class):
    return feed_class(
        title=Markup(feed.title).striptags(),
        link=(SITE_URL + "/"),
        feed_url=feed.feed_url,
        description=feed.description,
        subtitle=feed.subtitle,
    )


def _add_to_feed(
    feed: Atom1Feed | Rss201rev2Feed, post: schemas.Post, description: str, content: str
):
    feed.add_item(
        title=post.title,
        link=f"{SITE_URL}/posts/{post.id}",
        # link=post.link,
        unique_id=str(post.id),
        description=description,
        content=content,
        categories=None,
        author_name=post.author,
        pubdate=datetime.datetime.fromtimestamp(post.publication_date),
        updateddate=datetime.datetime.fromtimestamp(post.update_date),
    )


def create_atom_feed(feed: schemas.Feed):
    atom = _create_feed(feed, Atom1Feed)
    for post in feed.posts[::-1]:
        _add_to_feed(atom, post, post.description, post.content)

    return atom.writeString("UTF-8")


def create_rss_feed(feed: schemas.Feed):
    rss = _create_feed(feed, Rss201rev2Feed)
    for post in feed.posts[::-1]:
        _add_to_feed(rss, post, post.content, "")

    return rss.writeString("UTF-8")
