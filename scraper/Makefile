.PHONY: crawl-itviec crawl-topdev crawl-vietnamworks crawl-topcv crawl-linkedin dedupe details classify consolidate

crawl-itviec:
	.venv/bin/python -m crawlers.itviec

crawl-topdev:
	.venv/bin/python -m crawlers.topdev

crawl-vietnamworks:
	.venv/bin/python -m crawlers.vietnamworks

crawl-topcv:
	.venv/bin/python -m crawlers.topcv

crawl-linkedin:
	.venv/bin/python -m crawlers.linkedin

dedupe:
	.venv/bin/python step-02-dedupe.py

details:
	.venv/bin/python step-03-fetch-details.py

classify:
	.venv/bin/python step-04-filter-tech.py

consolidate:
	.venv/bin/python step-05-consolidate.py

extract:
	.venv/bin/python step-06-extract-with-llm.py

jev-classify:
	.venv/bin/python step-07-extract-with-jev.py
