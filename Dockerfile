FROM python:3.10.13-slim-bookworm

WORKDIR /app

COPY . /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    apt-get autoclean && \
    rm -rf /var/lib/apt/lists/* && \
    adduser --disabled-password --gecos '' caveman && \
    mkdir -p /app/uploads /app/config /app/logs && \
    chown -R caveman:caveman /app

USER caveman

ENV PATH="/home/caveman/.local/bin:${PATH}"
ENV FORWARDED_ALLOW_IPS="*"

RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y ecdsa && \
    pip install --upgrade pip

EXPOSE 8080

COPY --chown=caveman:caveman scripts/run.sh /app/scripts/run.sh
RUN chmod +x /app/scripts/run.sh

CMD ["/app/scripts/run.sh"]
