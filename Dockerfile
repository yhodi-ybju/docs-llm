FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    ccache \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
