in=python3
flags=

default:
	$(in) main.py example.kag

#test:
#	find ./test-cases -name '*.kag' | xargs python3 main.py

test:
	$(in) main.py test.kag


