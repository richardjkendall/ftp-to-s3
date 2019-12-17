FROM python:3.8-alpine

ADD requirements.txt .
ADD server.py .

RUN pip3 install -r requirements.txt

EXPOSE 10021/tcp
EXPOSE 60000-61000/tcp
CMD [ "python3", "./server.py" ]