FROM python:3.12-slim

WORKDIR /usr/lib/app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir dumb-init

COPY ./src ./src
COPY config.prod.yml ./config.prod.yml

ENV PYTHONPATH=./
ENTRYPOINT ["/usr/local/bin/dumb-init", "--"]
CMD ["python", "src/app.py", "-c", "config.prod.yml"]