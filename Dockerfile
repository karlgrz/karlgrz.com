FROM karlgrz/ubuntu-14.04-base-nginx
VOLUME [ "/var/log/nginx" ]
EXPOSE 8001

ADD root /

ADD site /srv

RUN rm /etc/nginx/sites-enabled/default \
	&& chmod 644 /etc/nginx/sites-enabled/*

RUN cd /srv && make publish

CMD ["nginx"]
