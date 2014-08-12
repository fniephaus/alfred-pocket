all: clean build

build:
	cd src ; \
	zip ../Pocket-for-Alfred.alfredworkflow . -r --exclude=*.DS_Store* --exclude=*.pyc*

clean:
	rm -f *.alfredworkflow