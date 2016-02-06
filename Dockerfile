FROM karlgrz/alpine-hugo
EXPOSE 8001

ADD site /site
WORKDIR /site

RUN rm -rf /site/public && hugo

CMD ["hugo", "server", "--bind=0.0.0.0", "--disableLiveReload=true", "--appendPort=false", "--port=8001", "--baseURL=https://karlgrz.com/"]
