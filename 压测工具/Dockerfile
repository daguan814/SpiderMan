FROM python:3.14-slim

WORKDIR /app

COPY main.py /app/main.py

ENV HOST=0.0.0.0
ENV PORT=8082
ENV OPEN_BROWSER=false

EXPOSE 8082

CMD ["python", "/app/main.py"]
