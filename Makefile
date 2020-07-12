PYTHON   = python3


build:
	$(PYTHON) setup.py build

sdist:
	$(PYTHON) setup.py sdist

clean:
	rm -rf build

distclean: clean
	rm -f MANIFEST .version
	rm -rf dist


.PHONY: build sdist clean distclean
