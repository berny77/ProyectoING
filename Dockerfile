FROM python:3.12

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download es_core_news_sm 

COPY . /app

CMD ["python", "Main.py"]