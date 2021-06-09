FROM python:3.7.9

ARG ssh_prv_key

RUN mkdir -p /root/.ssh
RUN echo "$ssh_prv_key" > /root/.ssh/TEMP.pem
RUN chmod 600 /root/.ssh/TEMP.pem

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt


COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0",  "--port=443", "--cert=adhoc"]