# You can set these variables from the command line, and also
# from the environment for the first two.

HTML_FILES := $(wildcard public/*.html)
JS_FILES := $(wildcard public/assets/*.js)
CSS_FILES := $(wildcard public/assets/*.css)

COMPRESSED_HTML := $(HTML_FILES:.html=.html.gz)
COMPRESSED_JS := $(JS_FILES:.js=.js.gz)
COMPRESSED_CSS := $(CSS_FILES:.css=.css.gz)

.PHONY: clean
clean:
	rm -rf public .build dist source/scripts/dist admin/dist/ __pycache__ api/__pycache__ api/**/__pycache__

.PHONY: fe
fe:
	frontend development

.PHONY: staging
staging: clean
	frontend staging

.PHONY: prod
prod: clean
	frontend production

.PHONY: compress
compress: $(COMPRESSED_HTML) $(COMPRESSED_JS) $(COMPRESSED_CSS)

%.gz: %
	gzip -c $< > $@

.PHONY: watch
watch:
	PYTHONUNBUFFERED=x frontend development watch

.PHONY: dev
dev: fe
	fastapi dev api/main.py

.PHONY: slots
slots:
	python -m api.sync_local peter@seattle-beauty-lounge.com

.PHONY: content
content:
	gdocsync source --email peter@seattle-beauty-lounge.com

.PHONY: install
install:
	pip install -e . -r requirements/dev.txt

.PHONY: js
js:
	npm run build

.PHONY: jsdev
jsdev:
	npm run dev

.PHONY: test
test:
	pytest api frontend

.PHONY: fmt
fmt:
	isort api frontend lib
	black api frontend lib

.PHONY: lint
lint:
	flake8 api frontend lib
	pylint api frontend lib
	pyright api frontend lib
	npx biome check --fix --unsafe source/scripts/*.jsx

.PHONY: gitconfig
gitconfig:
	git config user.name 'Peter Demin (bot)'
	git config user.email 'peterdemin@users.noreply.github.com'

.PHONY: push
push:
	git push -u origin +gh-pages

.PHONY: master
master:
	git checkout master

.PHONY: lock
lock:
	requirements lock

.PHONY: upgrade
upgrade:
	requirements upgrade

.PHONY: sync
sync:
	pip-sync requirements/dev.txt
	pip install -e .

.PHONY: ubuntu-install
ubuntu-install:
	sudo tools/ubuntu_install.sh
