Instrucciones para iniciar la tarea numero 1 de sistemas distribuidos

Primero se debe de descargar dependencias de dockers

sudo apt-get update

sudo apt install docker.io docker-compose -y

sudo systemctl start docker

sudo systemctl enable docker

sudo apt install docker-compose -y

sudo apt-get install docker-compose-plugin

sudo docker-compose up --build

nueva terminal

 sudo docker-compose exec sistema_cache python3 -c "import requests; print(requests.get('http://127.0.0.1:5000/generar_reporte').json())"

para reinciar docker

sudo docker-compose down

sudo docker-compose rm -f

sudo docker-compose up --build

para que jale mejor

sudo docker-compose down --volumes --remove-orphans


