PYPI_HOST = pypi.tuna.tsinghua.edu.cn
PYPI = https://$(PYPI_HOST)/simple

cybersearch_install:
	python3 -m pip install -U pip -i $(PYPI) --trusted-host $(PYPI_HOST)
    python3 -m pip install -e . -i $(PYPI) --trusted-host $(PYPI_HOST)
