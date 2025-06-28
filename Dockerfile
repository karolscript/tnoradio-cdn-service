FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
ENV FLASK_APP=cdn.py
EXPOSE 19000
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=19000"]