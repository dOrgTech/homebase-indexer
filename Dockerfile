FROM python:3.10

ARG PG_HOST
ARG PG_PORT
ARG PG_USER
ARG PG_PASSWORD
ARG PG_DB
ARG PG_SCHEMA

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
COPY registrydao .
COPY dipdup.yml .
RUN echo $'PG_HOST=${PG_HOST}\n\
PG_PORT=${PG_PORT}\n\
PG_USER=${PG_USER}\n\
PG_PASSWORD=${PG_PASSWORD}\n\
PG_DB=${PG_DB}\n\
PG_SCHEMA=${PG_SCHEMA}\n\' > .env
CMD ["dipdup", "-e", ".env", "run"]