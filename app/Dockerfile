FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Wiki wird als Volume eingebunden
ENV WIKI_PATH=/wiki
CMD ["python", "main.py"]
