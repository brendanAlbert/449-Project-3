SHELL := /bin/bash
init :
	sudo apt install --yes postgresql
	sudo -u postgres psql -c 'DROP DATABASE IF EXISTS kong'
	sudo -u postgres psql -c 'DROP USER IF EXISTS kong'
	sudo -u postgres psql -c "CREATE USER kong WITH ENCRYPTED PASSWORD 'kong'"
	sudo -u postgres psql -c 'CREATE DATABASE kong OWNER kong'
	sudo cp kong_copy.conf /etc/kong/kong.conf
	sudo kong migrations bootstrap
	ulimit -n 4096 && sudo kong start
	chmod +x kong_configuring.sh
	./kong_configuring.sh
	flask init
	foreman start -m all=3

startminio :
	chmod +x minio
	./minio server minio_data/

seedapi :
	chmod +x seedapi.sh
	./seedapi.sh
