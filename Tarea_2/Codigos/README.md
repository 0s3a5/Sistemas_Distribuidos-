En esta carpeta se incluyen todos loscodigo y carpetas necesarias para que 
se compile correctamente 

Cade destacar que el desrrollo de funcionalidades y especificaciones
se encuentran en el informe entregado.

En este readme estan las instrucciones para cambiar las configuraciones 
en caso de querer probar los cambios de memoria de cache y de politicas de remocion.

Instrucciones:

1) instalar dependencias de docker con:

sudo apt install docker.io docker-compose -y

2) -*Paso opcional en caso de no tener autorizacion*-

Dar permisos de usuario "sudo usermod -aG docker $0s3a5" cambiar por usuario

3) Instalar pandas

sudo apt install python3-pip -y

pip3 install pandas

Ahora para probar la funcionalidad se debe de ir a la carpeta de los archivos
cd codigos

1) Iniciar docker

sudo systemctl start docker

2) Permitir docker

sudo systemctl enable docker

3) Instalar docker compose en caso de no tenerlo

sudo apt-get install docker-compose-plugin

4) Ejecutar finalmente el docker

sudo docker compose up -build


4.1) para revisar en la segunda ventana se utiiza

sudo docker compose logs -f traffic-gen

para cambiar a modo consumidor se borra todo con sudo docker compose down -v

luego se hace 

sudo docker compose up --scale kafka-consumer=n
cambiando n por los consumidores que se quiera

para la segunda ventana se hace lo mismo

para cambiar a un sistema de fallas manual se hace

sudo docker compose up

y en la segunda ventana se hace sudo docker compose stop response-gen 
para levantarlo se hace sudo docker compose start response-gen 

para cambiar los consumidores y la falla rate se va a  generador de respuesta y se cambia el 0.0 por 0-3 o por 1.0

y finalmente si se quiere ver la spike se debe de sacar el "#" del final del codigo de generador de trafico
