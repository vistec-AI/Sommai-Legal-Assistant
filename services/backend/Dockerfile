FROM python:3.11

RUN apt-get update

COPY ./app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/src/app

ENV PYTHONPATH "/usr/src:${PYTHONPATH}"

COPY ./app .

EXPOSE 5000

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
