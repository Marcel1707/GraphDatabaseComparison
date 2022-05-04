FROM python:3.9.1
WORKDIR /usr/app/src
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY main.py ./
CMD [ "python", "./main.py" ]