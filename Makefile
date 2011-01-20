# ex: set tabstop=4 noexpandtab: 
VERSION = $(shell cat VERSION)
NAME=kickstarter
TAGVER = $(shell cat VERSION | sed -e "s/\([0-9\.]*\).*/\1/")

ifeq ($(VERSION), $(TAGVER))
        TAG = $(TAGVER)
else
        TAG = "HEAD"
endif


PYTHON=python
CHEETAH=cheetah
TEMPLATES=$(wildcard *.tmpl)
TEMPLATE_MODS=$(patsubst %.tmpl,%.py,$(TEMPLATES))
.SECONDARY: $(TEMPLATE_MODS)
KS=$(wildcard *.ks)

all: $(TEMPLATE_MODS)

%.py: %.tmpl
	$(CHEETAH) compile --settings='useStackFrames=False' $<


ks: $(TEMPLATES) configurations.yaml repos.yaml
	python kickstarter.py -c configurations.yaml -r repos.yaml

tag:
	git tag $(VERSION)

dist-bz2:
	git archive --format=tar --prefix=$(NAME)-$(VERSION)/ $(TAG) | \
		bzip2  > $(NAME)-$(VERSION).tar.bz2

dist-gz:
	git archive --format=tar --prefix=$(NAME)-$(VERSION)/ $(TAG) | \
		gzip  > $(NAME)-$(VERSION).tar.gz

dist: dist-bz2

clean:
	rm -f $(TEMPLATE_MODS)
	rm -f $(addsuffix .bak,$(TEMPLATE_MODS))
	rm -f *.pyc *.pyo
