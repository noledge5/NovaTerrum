FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Wiki wird als Docker Volume eingehängt:
#   docker run -v /volume1/NovaTerrum/wiki:/wiki ...
ENV WIKI_PATH=/wiki

EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/state || exit 1

CMD ["python", "main.py"]
