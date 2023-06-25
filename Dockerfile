FROM python:3.11.4

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]