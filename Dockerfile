FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

RUN pip install python-telegram-bot==13.15

COPY pricetracker.py .

CMD ["python", "pricetracker.py"]
