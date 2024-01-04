FROM python:3.9

RUN mkdir usr/app
WORKDIR usr/app

WORKDIR ..

COPY . .

RUN pip install -r requirements.txt

CMD python app.py
