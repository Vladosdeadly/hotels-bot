FROM python:3.8
COPY requirements.txt  /
RUN pip install -r requirements.txt 
RUN pip install pipenv
WORKDIR /src
COPY Pipfile /src
COPY Pipfile.lock /src
RUN pipenv install --deploy --system
RUN pipenv install --dev
COPY . /src
