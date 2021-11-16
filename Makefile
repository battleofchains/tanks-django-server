USERID := $$(id -u)
GROUPID := $$(id -g)
COMPOSE := CURRENT_UID=$(USERID):$(GROUPID) docker-compose -f local.yml
COMPOSE_PROD := CURRENT_UID=$(USERID):$(GROUPID) docker-compose -f production.yml
MANAGE := docker-compose -f local.yml run -u $(USERID):$(GROUPID) --rm django python manage.py
MANAGE_PROD := docker-compose -f production.yml run -u $(USERID):$(GROUPID) --rm django python manage.py
DJANGO := docker-compose -f local.yml run -u $(USERID):$(GROUPID) --rm django

build:
	$(COMPOSE) build

build-no-cache:
	$(COMPOSE) build --no-cache

up:
	$(COMPOSE) up

down:
	$(COMPOSE) down

create_user:
	$(MANAGE) createsuperuser
