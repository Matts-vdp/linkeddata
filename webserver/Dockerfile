FROM python:3.10-buster

RUN pip install sparqlWrapper
RUN pip install flask
RUN pip install matplotlib

COPY web.py .
COPY sparqlclient.py .
COPY templates templates

CMD ["python", "web.py"]