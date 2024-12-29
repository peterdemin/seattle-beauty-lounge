# You can set these variables from the command line, and also
# from the environment for the first two.

.PHONY: clean
clean:
	rm -rf public .build dist source/scripts/dist

.PHONY: fe
fe:
	python3 frontend.py

.PHONY: watch
watch:
	python3 frontend.py watch

.PHONY: dev
dev: fe
	fastapi dev api/main.py

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
	isort api
	black api

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
		--allow-unsafe \
		--autoresolve \
		--skip-constraints \
		--no-upgrade

.PHONY: upgrade
upgrade:
	pip-compile-multi \
		--autoresolve \
		--skip-constraints \
		--allow-unsafe

.PHONY: sync
sync:
	pip-sync requirements/dev.txt
