FROM redis:7.2.5-alpine

RUN mkdir -p /var/run/redis/
RUN chown root /var/run/redis/

CMD redis-server --unixsocket /var/run/redis/redis-server.sock --unixsocketperm 777 --save 60 1 --loglevel warning
