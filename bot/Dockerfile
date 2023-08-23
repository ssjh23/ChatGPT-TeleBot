FROM python:3.9.13
WORKDIR /app
COPY . /app/
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5000
ENV PYTHONUNBUFFERED 1
ENV USE_DOCKER=true

CMD ["python", "main.py"]