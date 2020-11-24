FROM python:3.7-slim-stretch
WORKDIR /usr/src/cryptoTracker/
COPY ./app.py /usr/src/cryptoTracker/
COPY ./requirements.txt /usr/src/cryptoTracker/
RUN pip install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
