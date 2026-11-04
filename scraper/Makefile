# Windows: make PY=.venv/Scripts/python <target>
PY ?= .venv/bin/python

.PHONY: crawl-itviec crawl-topdev crawl-vietnamworks crawl-topcv crawl-linkedin crawl-careerlink crawl-itnavi crawl-zalo crawl-momo redact ingest dedupe clean extract test

crawl-itviec:
	$(PY) -m crawlers.itviec

crawl-topdev:
	$(PY) -m crawlers.topdev

crawl-vietnamworks:
	$(PY) -m crawlers.vietnamworks

crawl-topcv:
	$(PY) -m crawlers.topcv

crawl-linkedin:
	$(PY) -m crawlers.linkedin

crawl-careerlink:
	$(PY) -m crawlers.careerlink

crawl-itnavi:
	$(PY) -m crawlers.itnavi

crawl-zalo:
	$(PY) -m crawlers.zalo

crawl-momo:
	$(PY) -m crawlers.momo

redact:
	$(PY) redact.py

ingest:
	$(PY) ingest.py

dedupe:
	$(PY) dedupe.py --raw data/redacted

clean:
	$(PY) clean.py

extract:
	$(PY) extract.py

test:
	$(PY) -m pytest tests -q
