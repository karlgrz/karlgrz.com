FROM karlgrz/ubuntu-14.04-base-go
EXPOSE 8001

ADD site /srv
WORKDIR /srv

RUN rm -rf /srv/public && hugo

CMD ["hugo", "server", "--bind=0.0.0.0", "--appendPort=false", "--port=8001", "--baseURL=https://karlgrz.com/"]
