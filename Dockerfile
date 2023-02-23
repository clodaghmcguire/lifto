FROM python:3.9-slim
LABEL maintainer="KCH Bioinformatics Team <kch-tr.KCHBioinformatics@nhs.net>"

WORKDIR /app
RUN apt-get update && apt-get -y install gcc libz-dev
COPY flask_app flask_app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENV FLASK_APP=flask_app
EXPOSE 5000
ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]
