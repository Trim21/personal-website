FROM python:3.7
LABEL MAINTAINER="Trim21 <Trim21me@gmail.com>"
EXPOSE 8000
WORKDIR /

COPY ./requirements/prod.txt /requirements.txt
RUN pip install -r /requirements.txt
COPY app /app

CMD ["uvicorn", "app.fast:app", \
        "--host", "0.0.0.0", \
        "--port", "8000", \
        "--workers", "3"]
