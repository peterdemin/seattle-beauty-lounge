FROM python:3.12

RUN mkdir -p /api
WORKDIR /
COPY requirements.txt /api
RUN pip install -r api/requirements.txt
COPY . /api

EXPOSE 80
CMD ["fastapi", "run", "--port", "80", "api/main.py"]
