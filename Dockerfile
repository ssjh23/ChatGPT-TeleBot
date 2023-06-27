FROM python:3.9.13
WORKDIR /app
COPY . /app/
RUN pip install --trusted-host pypi.python.org -r requirements.txt
RUN apt-get update
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y nodejs \
    npm   

RUN npm install -g nodemon

EXPOSE 5000
ENV PYTHONUNBUFFERED 1
ENV USE_DOCKER=true

CMD ["nodemon", "main.py"]