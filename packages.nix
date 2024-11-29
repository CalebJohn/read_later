{ pkgs ? import <nixpkgs> {} }:

{
  packageGenerator = pythonPackages: with pythonPackages; [
      fastapi
      feedgenerator
      httpx
      uvicorn
      readability-lxml
      alembic
      sqlalchemy
      markupsafe
      gunicorn
      jinja2
    ];
}
