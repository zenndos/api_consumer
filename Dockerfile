FROM python:3
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . /app
CMD python /app/api_server.py
