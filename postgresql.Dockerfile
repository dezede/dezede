FROM postgis/postgis:13-3.5

RUN localedef -i fr_FR -c -f UTF-8 -A /usr/share/locale/locale.alias fr_FR.UTF-8
ENV LANG fr_FR.utf8

COPY postgresql-init.sql /docker-entrypoint-initdb.d/
