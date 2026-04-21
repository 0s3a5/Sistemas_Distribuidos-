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

sudo docker-compose up --build

con esto se prueba la primera funcionalidad

si se quiere el informe en otra ventana de la terminal se pone

sudo docker-compose exec sistema_cache python3 -c "import requests; print(requests.get('http://127.0.0.1:5000/generar_reporte').json())"

5) Para cambiarlo se cierra docker

sudo docker-compose down

6) Se eliminan residuos

sudo docker-compose rm -f

*Cambiar datos*
Para cambiar tamaño de cache y la politica de remocion

1) Abrir como archivo de texto docker-compose.yml
   
2) cambiar cantidad de mb de 500 a lo que se estime conveniente

3) cambiar lfu por el que se estime, nosotros lo hicimos con lru y lfu

*cambiar simulacion de trafica*

1) meterse en carpeta generador_trafico
  
2) Abrir el archivo main.py como archivo de texto

3) cambiar el gato (#) ya que esta como comentario el trafico unifome
   si se quiere ocupar zipf se deja asi
   Si se quiere ocupar uniforme se pone comentario la funcion simular trafico que incluye zipf
