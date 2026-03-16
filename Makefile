HTML_FILES := $(wildcard public/*.html)
JS_FILES := $(wildcard public/assets/*.js)
CSS_FILES := $(wildcard public/assets/*.css)
E2E_BASE_URL ?= https://staging.seattle-beauty-lounge.com

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
	gzip -fnk $<

.PHONY: watch
watch:
	PYTHONUNBUFFERED=x frontend development watch

.PHONY: dev
dev: fe
	(sleep 3 && open http://localhost:8000/index.html)&
	python -m fastapi dev api/main.py

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

.PHONY: e2e
# Run E2E against an already-running make dev server with proxy_frontend disabled/enabled.
# Example:
#   make dev   # starts backend (and builds frontend into public/)
#   E2E_BASE_URL="http://127.0.0.1:8000" make e2e
e2e:
	@if [ ! -x node_modules/.bin/playwright ]; then \
		npm install; \
		npm exec playwright install; \
	fi
	E2E_BASE_URL="$(E2E_BASE_URL)" \
	npm run e2e

.PHONY: jstest
jstest:
	node source/scripts/testAvailability.js
	for test_file in admin/*.test.js; do \
		node $$test_file; \
	done

.PHONY: test
test:
	pytest api lib frontend --cov=api --cov=lib --cov-fail-under=70

.PHONY: fmt
fmt:
	isort api frontend lib
	black api frontend lib

.PHONY: lint-python
lint-python:
	flake8 api frontend lib
	pylint api frontend lib
	pyright api frontend lib

.PHONY: lint-js
lint-js:
	npx biome check --fix --unsafe source/scripts/*.jsx

.PHONY: lint
lint: lint-python lint-js

.PHONY: check
check: fmt lint test jstest

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

.PHONY: analytics
analytics:
	./tools/pull.sh
	gunzip -kf logs/seattle-beauty-lounge.com/*.gz
	ls logs/seattle-beauty-lounge.com/access.log* | grep -v \.gz | xargs goaccess -c -o analytics.html --log-format=COMBINED
	open analytics.html

.PHONY: ubuntu-install
ubuntu-install:
	sudo tools/ubuntu_install.sh
