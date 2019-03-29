FROM python:2.7-alpine as base

RUN apk --update add libpq
# prepare compiling environment as virtual package `build-dependencies`
RUN apk --update add --virtual build-dependencies \
  build-base \
  musl-dev \
  python2-dev \
  postgresql-dev \
  libffi-dev

RUN mkdir /var/log/dearbnb/
WORKDIR /var/www/dearbnb

RUN pip install --no-cache-dir pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system

# remove compiling environment `build-dependencies`
RUN apk del build-dependencies

COPY . .

########################################
# dev stage for conveinent development envrionment
FROM base as dev
RUN apk --update add --no-cache curl bash less
RUN apk --update add --no-cache postgresql-client redis

########################################
# release stage
FROM base as release
