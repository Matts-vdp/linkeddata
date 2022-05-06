FROM python:3.10-buster

RUN pip install sparqlWrapper
RUN pip install flask
RUN pip install matplotlib

WORKDIR /webserver

CMD ["python", "web.py"]