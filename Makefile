# Make file to deploy and do custom action on the proyect

up:
	docker-compose -p lintec -f ./docker/docker-compose.yml up -d
down:
	docker-compose -p lintec -f ./docker/docker-compose.yml down
build:
	docker-compose -p lintec -f ./docker/docker-compose.yml build --no-cache
deploy-up:
	touch docker/traefik/acme.json && chmod 600 docker/traefik/acme.json
	docker-compose -p lintec -f ./docker/docker-compose.yml down
	docker-compose -p lintec -f ./docker/docker-compose.deploy.yml up -d
deploy-down:
	docker-compose -p lintec -f ./docker/docker-compose.deploy.yml down
destroy:
	docker-compose -p lintec -f ./docker/docker-compose.yml down
	docker volume rm docker_odoo-db-data docker_odoo-web-data
restart:
	docker-compose -p lintec -f ./docker/docker-compose.yml restart
ssh:
	docker exec -it odoo_web_lintec /bin/bash
root:
	docker exec -it -u 0 odoo_web_lintec /bin/bash
update:
	docker exec -it -u 0 odoo_web_lintec odoo -u all
shell:
	docker exec -it odoo_web_lintec odoo shell -c /etc/odoo/odoo.conf -d odoo

