FROM ubuntu:16.04

RUN apt-get -y update

ENV POSTGRESV 9.5
RUN apt-get install -y postgresql-$POSTGRESV

RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip

ENV WORKDIR ./
ADD requirements.txt $WORKDIR/requirements.txt

RUN pip3 install -r requirements.txt

USER postgres

RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';" &&\
    createdb -E UTF8 -T template0 -O docker docker &&\
    /etc/init.d/postgresql stop

RUN echo "host all  all    0.0.0.0/0  trust" >> /etc/postgresql/$POSTGRESV/main/pg_hba.conf

RUN echo "listen_addresses='*'" >> /etc/postgresql/$POSTGRESV/main/postgresql.conf
RUN echo "synchronous_commit=off" >> /etc/postgresql/$POSTGRESV/main/postgresql.conf

EXPOSE 5432

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

USER root

ADD foroom/ $WORKDIR/foroom/
ADD foroom/schema.sql $WORKDIR/foroom/schema.sql

EXPOSE 5000

ENV PGUSER docker
ENV PGPASSWORD docker
ENV FLASK_APP foroom/main.py
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
CMD service postgresql start &&\
    cd $WORKDIR/foroom/ &&\
    psql -h localhost -U docker -d docker -f schema.sql -w &&\
    gunicorn -b 0.0.0.0:5000 --workers=8 main:app
