# Makefile for Twine game publishing.

.DEFAULT:; mkdocs $@

all: publish

publish: gh-deploy

