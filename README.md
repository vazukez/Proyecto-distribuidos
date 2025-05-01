# Proyecto-distribuidos

Proyecto semestral de el ramo sistema distribuidos realizado por Alejandro Saldías y Matias Vasquez.

# Distribucion de archivos

Cada carpeta del github contiene el codigo correspondiente a uno de los servicios montados en docker, al archivo python con la logica de cada uno se añaden un documento txt con los requerimientos del servicio, tipo librerias necesarias a instalar, y un archivo dockerfile con las instrucciones a ejecutarse al hacer el contenedor en docker. En cuanto al archivo docker-compose.yml es el archivo usado para montar todos los servicios de forma individual bajo la misma red para que puedan comunicarse sin problemas entre si, este archivo considera solo los tres archivos dentro de las carpetas de cada servicio por lo que para mantener el orden y evitar errores se dejan las carpetas de cada codigo lo mas minimilistas posibles , solo con lo necesario para el montaje. El archivo docker-compose.yml tambien tiene la logica para el cuarto contenedor que es el sistema de almacenamiento que corresponde a una base de datos Mongo. Finalmenre se incluyo un archivo json con todos los eventos registrados por el grupo atraves del scraper para su rapida implementacion.

#  Sistema de almacenamiento:

Para el sistema de almacenamiento se decidio usar una base de datos Mongo, en cuanto al docker generado atraves del docker-compose no es necesario el implementar ningun tipo de cambio para correrlo, en la experiencia del grupo una vez formado el contenedor mongo no es necesario el volver a cambiarle nada y incluso si se apaga el contenedor la data de los eventos deberia permanecer. En este caso se  tomo en cuenta que al ser formado por primera vez el contenedor este vendra vacio se incluyo un json con la data necesaria para poder usarlo, para esto se debe tener el json en el equipo con su direccion en este y hacer uso de los siguientes comandos:

Paso 1: Copiar el archivo al contenedor.

En la terminal con docker ejecutar:
docker cp "Direccion archivo con eventos.json" mongo:/data/"Nombre archivo.json"

Paso 2: Importar la data a la base de datos.

Se entra al contenedor con:
docker exec -it mongo bash

Una vez dentro se ejecuta el importador:
mongoimport --db Waze --collection Peticiones --jsonArray --file /data/"Nombre archivo.json"

Paso 3(Opcional): Verificar la importacion.

Aun en el contenedor, iniciar consola mongo:
mongosh

Adentro realizar los siguientes comandos:
- Para acceder a la base de datos especifica:
use Waze
- Para detectar la cantidad de eventos dentro de la base de datos:
db.Peticiones.countDocuments()

# Scraper:

Para el scraper no se añadio ningun campo en especial al contenedor en docker por lo que al subir el contenedor deberia funcionar sin problemas. El scraper consigue eventos de Waze cada 30 segundos y los almacena en mongo por lo que para su funcionamiento el contenedor de Mongo debe estar funcionando previamente.

# Generador de trafico:

Para el generador de trafico si se añadieron campos especiales a este, la mayoria de campos son relacionados a la configuracion para su funcionamiento pero hay un par que son importantes para la realizacion de experimentos:

- --dist: Se refiere a el tipo de distribucion que usara el generador, este tiene dos opciones para su uso, poisson y uniform.
- --low y --high: estos son los valores que se usaran para la distribucion uniform de ser usada.
- --n: este sera el numero total de traficos de consultas que se realizara.

# Cache:

Para el cache se debe tener en cuenta que es de memoria volatil, en otras palabras una vez se apage el contenedor del cache este se borrara a diferencia de la base de datos que permanece incluso apagada. Tambien se incluyeron valores especiales a el cache para su montaje de docker que pueden ser cambiados para su experimentacion:

- --policy: Este valor indica el tipo de politica que usara el cache, tiene dos opciones que son: lru y lfu.
- --size: Este valor indica que tan grande sera el cache, funciona tal que si el tamaño es de 100 esas seran 100 entradas o eventos que podra guardar.


Uso del sistema en la experiencia de los alumnos:

Se utilizo en gran medida Visual studio code y docker desktop, con visual studio se trabajo en la carpeta con los codigos y archivos y fue desde donde se fue modificando los valores, con esto en mente se hizo uso de extensiones de la aplicacion para correr automaticamente los servicios por separado cada vez que era necesario probar un nuevo valor desde el archivo docker-compose. En cuanto a la visualizacion de logs y comportamiento de los servicios ya montados se uso docker desktop ya que no se tenia una gran familiaridad con el uso de desktop desde terminal.

  
