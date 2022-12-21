FROM python:3.10

WORKDIR /usr/src/chunker

COPY ./csv_chunker.py /usr/src/chunker/csv_chunker.py

RUN pip install pandas dask

# Uncomment for running behind proxy:
# RUN curl --proxy socks5h://localhost:8080 -O https://files.pythonhosted.org/packages/bd/11/293dd436aea955d45fc4e8a35b6ae7270f5b8e00b53cf6c024c83b657a11/PySocks-1.7.1.tar.gz && \
#         tar -xf PySocks-1.7.1.tar.gz && \
#         cd PySocks-1.7.1 && \
#         python3 setup.py install
# RUN pip install pandas dask --proxy socks5h://127.0.0.1:8080

CMD [ "python", "./csv_chunker.py" ]