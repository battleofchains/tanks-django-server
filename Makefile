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

up: load_fixtures
	$(COMPOSE) up

up[daemon]:
	$(COMPOSE) up -d

stop:
	$(COMPOSE) stop

down:
	$(COMPOSE) down

create_user:
	$(MANAGE) createsuperuser

shell:
	$(MANAGE) shell_plus

makemigrations:
	$(MANAGE) makemigrations

migrate:
	$(MANAGE) migrate

load_fixtures:
	$(MANAGE) loaddata tank_types projectile_types maps battle_types --settings=config.settings.local
