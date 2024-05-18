FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=0

RUN mkdir /app
WORKDIR /app

COPY . /app

RUN pip install .

ENTRYPOINT ["python", "-m" ,"khinsider.py"]