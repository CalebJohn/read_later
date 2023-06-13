FROM python:3.10-alpine

RUN mkdir -p /app/data
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src src
COPY static static
COPY templates templates

EXPOSE 5000

CMD [ "gunicorn", "src.main:app", "--worker-class", \
      "uvicorn.workers.UvicornWorker",  "-b", "0.0.0.0:5000" ]
