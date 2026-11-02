# Windows: make PY=.venv/Scripts/python <target>
PY ?= .venv/bin/python

.PHONY: crawl-itviec crawl-topdev crawl-vietnamworks crawl-topcv crawl-linkedin crawl-careerlink crawl-itnavi crawl-zalo crawl-momo dedupe details classify consolidate

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

dedupe:
	$(PY) step-02-dedupe.py

details:
	$(PY) step-03-fetch-details.py

classify:
	$(PY) step-04-filter-tech.py

consolidate:
	$(PY) step-05-consolidate.py

extract:
	$(PY) step-06-extract-with-llm.py

jev-classify:
	$(PY) step-07-extract-with-jev.py
