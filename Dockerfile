FROM python:3.10

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

WORKDIR /app
RUN apt-get update && apt-get install -y libvips42
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
EXPOSE 5000

CMD ["flask", "run"]
