all: clean build

build:
	cd src ; \
	zip ../Pocket-for-Alfred.alfredworkflow . -r --exclude=*.DS_Store* --exclude=*.pyc* --exclude=.coverage --exclude=test*

clean:
	rm -f *.alfredworkflow

update-lib:
	/usr/bin/python -m pip install --target src --upgrade Alfred-Workflow
	rm -rf src/Alfred_Workflow-*.*info/
