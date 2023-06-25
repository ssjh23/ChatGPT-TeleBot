# ChatGPT-TeleBot
Telegram Bot for using ChatGPT in python

**** DO NOT COMMIT KEYS ****

Accidentally committed key count: 4

Docker terminal command for development 
```
docker run -dp 127.0.0.1:3000:3000 \
-w /app --mount type=bind,src="$(pwd)",target=/app \
python:3.9.13 \
sh -c "pip install --trusted-host pypi.python.org -r requirements.txt && apt-get update \
&& apt-get upgrade -y && \
apt-get install -y nodejs \
npm  && \
npm install -g nodemon && \
nodemon main.py"
```
