FROM python:3.10-slim
LABEL authors="diego"

WORKDIR /app
COPY . /app

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
RUN pip install  -r requirements.txt

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]