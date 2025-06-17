FROM python:3.11

WORKDIR /app

COPY wheels/ /wheels
COPY . .

RUN pip install --no-index --find-links=/wheels -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
