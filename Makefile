# ex: set tabstop=4 noexpandtab: 
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

clean:
	rm -f $(TEMPLATE_MODS)
	rm -f $(addsuffix .bak,$(TEMPLATE_MODS))
	rm -f *.pyc *.pyo
