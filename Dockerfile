FROM ubuntu:latest
MAINTAINER Andrew Marcuse "fileformat@gmail.com"

RUN apt-get update -y && \
    apt-get install -y python-pip python-psycopg2 postgresql
    
RUN pip install WebOb Paste webapp2

COPY . /app

RUN \
    service postgresql start && \
    su postgres -c "createuser --superuser root" && \
    psql --echo-queries --dbname=postgres --file=/app/dbinit.sql
    
#    createdb rxp_db && \
#    psql --echo-queries --dbname=rxp_db --file=/app/dbinit.sql
 
ENV DATABASE_URL=postgresql://rxp_user:secret@localhost:5432/rxp_db
ENV COMMIT=$COMMIT
ENV LASTMOD=$LASTMOD

WORKDIR /app
CMD ./server.sh
