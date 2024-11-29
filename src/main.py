from datetime import datetime
import os
from typing import Annotated
from urllib.parse import unquote

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from sqlalchemy.orm import Session

import crud, extractor, feed_gen, models, schemas
from database import engine, get_db
from metadata import SITE_HOST, SITE_PORT, APP_DIR

# Create the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(APP_DIR, "templates"))

@app.get("/feeds/{public_hash}.atom.xml")
def get_atom_feed(public_hash: str, db: Session = Depends(get_db)):
    feed = crud.get_feed_by_hash(db, public_hash)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    data = feed_gen.create_atom_feed(feed)
    return Response(content=data, media_type="application/xml")
    # If we first save the file to disk we can return a FileResponse instead
    # https://fastapi.tiangolo.com/advanced/custom-response/#fileresponse


@app.get("/feeds/{public_hash}.rss")
def get_rss_feed(public_hash: str, db: Session = Depends(get_db)):
    feed = crud.get_feed_by_hash(db, public_hash)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    data = feed_gen.create_rss_feed(feed)
    return Response(content=data, media_type="application/rss+xml")


@app.get("/feeds/{public_hash}", response_class=HTMLResponse)
async def read_feed(request: Request, public_hash: str, db: Session = Depends(get_db)):
    feed = crud.get_feed_by_hash(db, public_hash)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    posts = [(post.title, post.link, datetime.fromtimestamp(post.update_date).isoformat(' ')) for post in feed.posts[::-1]]
    return templates.TemplateResponse("feed.html", {"request": request, "posts": posts})


@app.post("/feeds/", response_model=schemas.Feed)
def post_new_feed(new_feed: schemas.FeedNew, db: Session = Depends(get_db)):
    """
    For users that want to create a custom feed (their own title, link, subtitle, description)
    """
    feed = crud.get_feed_by_secret(db, new_feed.secret)
    if feed:
        return feed
    return crud.create_feed(db, new_feed)


@app.post("/posts/", response_model=schemas.Post)
def post_new_item(new_post: schemas.PostNew, needs_extracting: bool = True, user_agent: Annotated[str, None, Header()] = None, db: Session = Depends(get_db)):
    """
    Updates the feed that matches the supplied secret
    """
    feed = crud.get_feed_by_secret(db, new_post.secret)
    if feed is None:
        feed = crud.create_empty_feed(db, new_post)
        if feed is None:
            raise Exception("Cannot create new feed")

    content = new_post.content
    if not content and new_post.link:
        content = extractor.fetch_document(new_post.link, user_agent)
        if not content:
            content = new_post.link

    if needs_extracting or not new_post.title:
        title, extracted = extractor.extract_document(content)
    if needs_extracting:
        content = extracted
    if not new_post.title:
        new_post.title = Markup(title).striptags()

    new_post.content = content

    post = crud.create_post(db, new_post, feed.id)

    crud.enforce_storage_limits(db, feed)

    if post is None:
        raise HTTPException(status_code=403, detail="Must provide correct secret")

    return post


@app.get("/posts/")
def post_new_item_hack(raw_url: str, secret: str, user_agent: Annotated[str, None, Header()] = None, db: Session = Depends(get_db)):
    """
    This is a hack to get around content security policy from websites.

    IT IS NOT SECURE.

    It is necessary to save with a bookmarklet. A more secure method would use a browser extension.
    """
    url = unquote(raw_url)
    new_post = schemas.PostNew(
        link=url, secret=secret, publication_date=int(datetime.utcnow().timestamp())
    )
    post_new_item(new_post, True, user_agent, db)
    return RedirectResponse("/success")


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    """
    The posts/:id endpoint is a wrapper around linking the actual site. It's not strictly necessary, but it is in place to trick feed apps into thinking this is a new post (for feed apps that dedup based on url.
    """
    post = crud.get_post_by_id(db, id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return RedirectResponse(post.link)


@app.get("/")
def landing_page():
    return FileResponse(os.path.join(APP_DIR, "static/index.html"))

@app.get("/save")
def landing_page():
    return FileResponse(os.path.join(APP_DIR, "static/save.html"))

@app.get("/success")
def landing_page():
    return FileResponse(os.path.join(APP_DIR, "static/success.html"))


@app.get("/favicon.ico")
def landing_favicon():
    return FileResponse(os.path.join(APP_DIR, "static/favicon.ico"))


app.mount("/favicons", StaticFiles(directory=os.path.join(APP_DIR, "static"), html=True), name="favicons")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=SITE_HOST, port=int(SITE_PORT), reload=True)
