DIR_VENV		:=	venv
VER_PY			:=	3.10

DIR_BIN			:=	$(DIR_VENV)/bin
DIR_SITE		:=	$(DIR_VENV)/lib/python$(VER_PY)/site-packages

CMD_ISORT		:=	$(DIR_BIN)/isort
CMD_PIP			:=	$(DIR_BIN)/pip$(VER_PY)
CMD_PUDB		:=	$(DIR_BIN)/pudb
CMD_PYLINT		:=	$(DIR_BIN)/pylint

LIB_CLICK		:=	$(DIR_SITE)/click/__init__.py
LIB_PYUSB		:=	$(DIR_SITE)/usb/__init__.py

SCR_PRINTED		:=	printed.py
DIR_LIBRARY		:=	lib


.PHONY: help
help:
	@echo "printed makefile"
	@echo
	@echo
	@echo "requirements         install requirements"
	@echo "requirements-dev     install requirements for developing"
	@echo "requirements-dbg     install requirements for debugging"
	@echo
	@echo "sort                 run $(CMD_ISORT) on $(SCR_PRINTED)"
	@echo "lint                 run $(CMD_PYLINT) on $(SCR_PRINTED)"


$(DIR_VENV):
	python$(VER_PY) -m venv "$(DIR_VENV)"
	$(CMD_PIP) install -U pip

$(LIB_CLICK) $(LIB_PYUSB): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements.txt"

$(CMD_ISORT) $(CMD_PYLINT): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements-dev.txt"

$(CMD_PUDB): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements-dbg.txt"

.PHONY: requirements
requirements: $(LIB_CLICK) $(LIB_PYUSB)

.PHONY: requirements-dev
requirements-dev: $(CMD_ISORT) $(CMD_PYLINT)

.PHONY: requirements-dbg
requirements-dbg: $(CMD_PUDB)


define _sort
	$(CMD_ISORT) \
		--combine-star \
		--force-sort-within-sections \
		--py "$(subst .,,$(VER_PY))" \
		--line-width="79" \
		--multi-line "VERTICAL_HANGING_INDENT" \
		--trailing-comma \
		--force-grid-wrap 0 \
		--use-parentheses \
		--ensure-newline-before-comments \
			$(1)
endef

.PHONY: sort
sort: requirements-dev
	$(call _sort,"$(SCR_PRINTED)" "$(DIR_LIBRARY)")


define PYLINT_MESSAGE_TEMPLATE
{C} {path}:{line}:{column} - {msg}
  ↪  {category} {module}.{obj} ({symbol} {msg_id})
endef
export PYLINT_MESSAGE_TEMPLATE

define _lint
	$(CMD_PYLINT) \
		--disable "C0111" \
		--msg-template="$$PYLINT_MESSAGE_TEMPLATE" \
		--output-format="colorized" \
			$(1)
endef

.PHONY: lint
lint: requirements-dev
	$(call _lint,"$(SCR_PRINTED)" "$(DIR_LIBRARY)")

