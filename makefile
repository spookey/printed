CMD_VENV		:=	virtualenv
DIR_VENV		:=	venv
VER_PY			:=	3.7

CMD_ISORT		:=	$(DIR_VENV)/bin/isort
CMD_PIP			:=	$(DIR_VENV)/bin/pip$(VER_PY)
CMD_PYLINT		:=	$(DIR_VENV)/bin/pylint

DIR_SITE		:=	$(DIR_VENV)/lib/python$(VER_PY)/site-packages
LIB_CLICK		:=	$(DIR_SITE)/click/__init__.py
LIB_PYUSB		:=	$(DIR_SITE)/usb/__init__.py


SCR_PRINTED		:=	printed.py


.PHONY: help
help:
	@echo "printed makefile"
	@echo
	@echo
	@echo "requirements         install requirements"
	@echo "requirements-dev     install requirements for developing"
	@echo
	@echo "sort                 run $(CMD_ISORT) on $(SCR_PRINTED)"
	@echo "lint                 run $(CMD_PYLINT) on $(SCR_PRINTED)"


$(DIR_VENV):
	$(CMD_VENV) -p "python$(VER_PY)" "$(DIR_VENV)"

$(LIB_CLICK) $(LIB_PYUSB): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements.txt"

.PHONY: requirements
requirements: $(LIB_CLICK) $(LIB_PYUSB)


$(CMD_ISORT) $(CMD_PYLINT): $(DIR_VENV)
	$(CMD_PIP) install -r "requirements-dev.txt"

.PHONY: requirements-dev
requirements-dev: $(CMD_ISORT) $(CMD_PYLINT)


define _sort
	$(CMD_ISORT) -cs -fss -m=5 -y -rc $(1)
endef

.PHONY: sort
sort: requirements-dev
	$(call _sort,"$(SCR_PRINTED)")


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
	$(call _lint,"$(SCR_PRINTED)")

