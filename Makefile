# Copyright 2018 SPARKL Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Invoke with PYTHON_VERSION=2 (default) or 3
PYTHON_VERSION ?= 2
ifeq ($(PYTHON_VERSION), 2)
PYTHON := python
PEP8 := pep8
PYLINT := pylint
PIP := pip
PYDOC := pydoc
else
PYTHON := python3
PEP8 := pycodestyle
PYLINT := pylint
PIP := pip3
PYDOC := pydoc3
endif

VERSION := $(shell git describe --tags --long --abbrev=1)
PY_VERSION := $(shell git describe --tags --abbrev=0)

########################
# DEFAULT TARGET IS HELP
########################
.PHONY: default
default: help ;

#################################
# DEPENDENCIES DIFFER IN PYTHON 3
#################################
ifeq ($(PYTHON_VERSION), 2)
DEPS := \
	argparse \
	certifi \
	elasticsearch \
	pep8  \
	psutil \
	pylint \
	pytest \
	requests \
	websocket-client \
	pytest_localserver
else
DEPS := \
	argparse \
	certifi \
	elasticsearch \
	pycodestyle \
	psutil \
	pylint \
	pytest \
	requests \
	websocket-client \
	pytest_localserver
endif

.PHONY: deps
deps:
ifeq  '$(shell which $(PIP))'  ''
	@echo "Missing $(PIP), required for compile target"
	@echo "Consider '[apt-get|brew] install python-$(PIP)'"
endif
ifeq  '$(shell which pandoc)'  ''
	@echo "Missing pandoc, required for 'rel' target"
	@echo "Consider '[apt-get|brew] install pandoc'"
endif
	@$(PIP) install --user -q $(DEPS)

######
# LINT
######
.PHONY: lint
lint:
	@echo Running $(PEP8)
	@$(PYTHON) -m $(PEP8) sparkl_cli
	@echo Running $(PYLINT)
	@$(PYTHON) -m $(PYLINT) --ignore=test sparkl_cli

#########
# COMPILE
#########
# Note the -v displayed version is in the form v0.0.0-n-hash
.PHONY: compile
compile:
	@$(PYTHON) -m compileall sparkl_cli
	@echo ${VERSION} > sparkl_cli/version.txt

.PHONY: clean_compile
	@find . -name "*.pyc" -exec rm {} \;

######
# DOCS
######
.PHONY: docs
docs:
	@echo "Please use $(PYDOC). For example:"
	@echo "  $(PYDOC) sparkl_cli"
	@echo "  $(PYDOC) sparkl_cli.cmd_call"
	@echo

######
# TEST
######
.PHONY: test
test: TEST_SSE TEST_USER TEST_PASS
	@$(PYTHON) -m pytest --ignore=sparkl_cli/test/data

.PHONY: TEST_SSE
ifdef TEST_SSE
TEST_SSE: ;
else
TEST_SSE:
	$(error Must set env var: $@)
endif

.PHONY: TEST_USER
ifdef TEST_USER
TEST_USER: ;
else
TEST_USER:
	$(error Must set env var: $@)
endif

.PHONY: TEST_PASS
ifdef TEST_PASS
TEST_PASS: ;
else
TEST_PASS:
	$(error Must set env var: $@)
endif

#########
# RELEASE
#########
# Note the Python version is in form 0.0.0 only, where we rely
# on setuptools to normalise and remove the leading 'v'.
.PHONY: rel
rel: clean compile
ifeq  '$(shell which pandoc)'  ''
	$(error "Missing pandoc. Consider '[apt-get|brew] install pandoc'")
else
	@sed s/{{version}}/\"${PY_VERSION}\"/ setup.py.src > setup.py
	@pandoc -o README.txt README.md
	@$(PYTHON) setup.py sdist
endif

.PHONY: clean_rel
clean_rel:
	@rm -f setup.py README.txt MANIFEST
	@rm -rf dist

#########
# INSTALL
#########
.PHONY: install
install: rel
	@sudo -H $(PIP) install $(firstword $(wildcard dist/*.gz))

###########
# UNINSTALL
###########
.PHONY: uninstall
uninstall:
	@sudo -H $(PIP) uninstall sparkl_cli

#######
# CLEAN
#######
.PHONY: clean
clean: clean_compile clean_rel ;

######
# HELP
######
.PHONY: help
help:
	@echo "SPARKL CLI Makefile"
	@echo "-------------------"
	@echo "Using $(PYTHON) because PYTHON_VERSION=$(PYTHON_VERSION)"
	@echo
	@echo "Specify one or more targets as follows:"
	@echo
	@echo "  clean"
	@echo "    removes all built artefacts including release"
	@echo
	@echo "  compile"
	@echo "    Compiles sources"
	@echo
	@echo "  lint"
	@echo "    Runs $(PEP8) and $(PYLINT) against sources"
	@echo
	@echo "  deps"
	@echo "    installs dependencies using $(PIP)"
	@echo
	@echo "  docs"
	@echo "    explains how to view code documentation"
	@echo
	@echo "  help"
	@echo "    shows this help"
	@echo
	@echo "  install"
	@echo "    installs the release globally using 'sudo -H $(PIP) install'"
	@echo
	@echo "  rel"
	@echo "    creates a release in the 'dist' directory using 'setuptools'"
	@echo
	@echo "  test"
	@echo "    runs tests using 'pytest' (see below)"
	@echo
	@echo "  uninstall"
	@echo "    uninstalls the release globally using 'sudo -H $(PIP) uninstall"
	@echo
	@echo "Tests require the following environment variables to be set:"
	@echo "  TEST_SSE  - the url of the SPARKL node to be used"
	@echo "  TEST_USER - the user name"
	@echo "  TEST_PASS - user password"
	@echo
	@echo "  For example:"
	@echo "  $$ TEST_SSE=http://localhost:8000" \
		  "TEST_USER=user@test.com" \
		  "TEST_PASS=some_secret" \
		  "make test"
	@echo
