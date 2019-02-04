repository = hub.karlgrz.com
image = karlgrz_web 

docker: docker_build

docker_build:
	docker build -t $(repository)/$(image) .

push:
	docker push $(repository)/$(image)

run:
	docker run -d --name $(image) -p 8001:8001 $(repository)/$(image)

stop:
	docker stop $(image)

rm:
	docker rm $(image)

restart: stop rm run

rebuild: docker

logs:
	docker logs $(image)

certs:
	sudo certbot --manual certonly -d *.$(domain) -d $(domain) --agree-tos --manual-public-ip-logging-ok --preferred-challenges dns-01 --server https://acme-v02.api.letsencrypt.org/directory
