PYTHON   = python3


build:
	$(PYTHON) setup.py build

test:
	$(PYTHON) setup.py test

sdist:
	$(PYTHON) setup.py sdist

clean:
	rm -rf build
	rm -rf tests/.pytest_cache

distclean: clean
	rm -f MANIFEST .version
	rm -rf dist


.PHONY: build test sdist clean distclean
