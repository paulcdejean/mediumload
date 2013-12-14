#!/usr/bin/python
import mediumwebsite
import sys

url = sys.argv[1]

test_site = mediumwebsite.mediumwebsite(url)
test_site.start()

