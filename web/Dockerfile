FROM python:3.11-buster as builder

ENV TZ=Asia/Yekaterinburg
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV APP /app

WORKDIR $APP
COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

WORKDIR $APP

ENV API_PORT 8000
EXPOSE $API_PORT

CMD uvicorn src.main:app --host "0.0.0.0" --port $API_PORT

