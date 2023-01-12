FROM python:3.10
WORKDIR /web
COPY . .
RUN pip3 install -r requirements.txt
CMD ["python3", "app.py"]