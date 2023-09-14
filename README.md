Read Later
==========

Read Later is a website archival and reading tool. Put simply, it is pocket (or wallabag) meets RSS. 

The basic usage is
1. Generate a Feed (only needs to be done once
    1. Save the Feed URL into your Feed reader
    2. (optional) Bookmark the Save URL
    3. (optional) Save the bookmarklet for storing websites
2. Use either the save page or the bookmarklet to store websites
3. View them later in your Feed reader!

Read Later works by saving website data (title, URL, stripped content) to a database with an associated feed. When requesting feed contents (atom or rss), Read Later will assemble a feed based on what's in the database.

Read Later is currently hosted on a free tier with limited data storage, so feed items will be periodically removed as space becomes filled. It removes items oldest items first, so don't rely on Read Later as a storage service, your feed reader should be doing that.

# API docs

TODO: Generate and/or view swagger docs

# Development
```
uvicorn src.main:app
```

This is not an actively managed project. It was created for personal use and will continue to be supported only as long as I continue to use it (and limited to the extent that I use it).

