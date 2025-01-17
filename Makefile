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
	rm -rf public .build dist source/scripts/dist __pycache__ api/__pycache__ api/**/__pycache__

.PHONY: fe
fe:
	python3 frontend.py development

.PHONY: staging
staging: clean
	python3 frontend.py staging

.PHONY: production
production: clean
	python3 frontend.py production

.PHONY: compress
compress: $(COMPRESSED_HTML) $(COMPRESSED_JS) $(COMPRESSED_CSS)

%.gz: %
	gzip -c $< > $@

.PHONY: watch
watch:
	python3 -u frontend.py development watch

.PHONY: dev
dev: fe
	fastapi dev api/main.py

.PHONY: slots
slots:
	python -m api.sync_local peter@seattle-beauty-lounge.com

.PHONY: content
content:
	gdocsync source

.PHONY: install
install:
	pip install -r requirements/dev.txt

.PHONY: js
js:
	npm run build

.PHONY: jsdev
jsdev:
	npm run dev

.PHONY: test
test:
	pytest api

.PHONY: fmt
fmt:
	isort api frontend.py
	black api frontend.py

.PHONY: lint
lint:
	flake8 api frontend.py
	pyright api frontend.py
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
	pip-compile-multi \
		--use-cache \
		--allow-unsafe \
		--autoresolve \
		--skip-constraints \
		--no-upgrade

.PHONY: upgrade
upgrade:
	pip-compile-multi \
		--use-cache \
		--autoresolve \
		--skip-constraints \
		--allow-unsafe

.PHONY: sync
sync:
	pip-sync requirements/dev.txt
