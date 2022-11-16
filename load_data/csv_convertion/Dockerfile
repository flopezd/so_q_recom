FROM golang:1.19

WORKDIR /usr/src/converter

RUN git clone https://github.com/SkobelevIgor/stackexchange-xml-converter
RUN cd stackexchange-xml-converter/ && go build

CMD ["stackexchange-xml-converter/stackexchange-xml-converter", "-result-format=csv", "-source-path=xml", "-store-to-dir=csv"]