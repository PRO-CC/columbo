.PHONY: install
install:
	sudo apt install python3-pip
	sudo apt install -y sqlite3
	python3 -m pip install -r requirements.txt