FROM python:3.10

WORKDIR /usr/app/

COPY . .

RUN pip install -r requirements.txt

CMD python /usr/app/api/app.py