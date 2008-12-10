# You can specify what Python interpreter to use by running
#   ``make PYTHON=_interp_``.
PYTHON = python

new:
	$(PYTHON) build/build.py --cache=pydotorg.cache -v -d data -o out -r images,styles,files,js

serve:
	$(PYTHON) build/run-server.py --fork

clean:
	rm -fr out/*

