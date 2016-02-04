FROM karlgrz/ubuntu-14.04-base-go
EXPOSE 8001

ADD root /

ADD site /srv
WORKDIR /srv

RUN rm -rf /srv/public && hugo

CMD ["hugo", "server", "--bind", "0.0.0.0", "--port", "8001"]
