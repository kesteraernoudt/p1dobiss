FROM python:3

WORKDIR /usr/src/p1dobiss

ADD p1server.py .
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "./p1server.py" ]
