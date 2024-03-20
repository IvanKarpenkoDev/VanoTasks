FROM python:3.11
WORKDIR /usr/src/personalised_nudges
COPY . .
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
CMD ["alembic", "upgrade", "head"]
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
