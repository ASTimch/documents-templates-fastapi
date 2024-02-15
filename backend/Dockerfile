FROM python:3.10

RUN echo "deb http://deb.debian.org/debian bookworm main contrib" | tee /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends libreoffice-writer
RUN apt-get install -y libreoffice-java-common \
    ttf-mscorefonts-installer \
    poppler-utils \
    # очистка кэша установки пакетов (удаление из слоя контейнера)
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /templdoc

WORKDIR /templdoc

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN chmod a+x /templdoc/startup_scripts/*.sh

# CMD ["/templdoc/startup_scripts/app.sh"]
# CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]