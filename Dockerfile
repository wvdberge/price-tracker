FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

RUN pip install requests playwright

COPY pricetracker.py .

CMD ["python", "pricetracker.py"]
