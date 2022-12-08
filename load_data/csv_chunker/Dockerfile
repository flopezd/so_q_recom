FROM python:3.10

WORKDIR /usr/src/chunker

COPY ./csv_chunker.py /usr/src/chunker/csv_chunker.py

RUN pip install pandas

CMD [ "python", "./csv_chunker.py" ]