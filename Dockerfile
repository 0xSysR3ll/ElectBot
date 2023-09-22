FROM python:3-slim-bullseye
# ARG mariadb_version=11.1.2

RUN apt-get update && apt-get upgrade -y --no-install-recommends && apt install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | bash

RUN apt-get update --no-install-recommends && apt install -y \
    libmariadb-dev \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python3", "-u", "electbot.py"]
