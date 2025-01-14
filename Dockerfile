FROM python:3.10.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV FLASK_APP="docminer/app.py"

CMD ["python", "docminer/app.py"]