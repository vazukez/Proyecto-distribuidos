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

Apartir de la entrega 2 se considera que se realizaron mjoras para el soporte de errores en el generado ademas de mejorar su visualizacion mostrando cosas como sus operaiones o latncia para poder tener estos datos luego a consideracion en futuros analisis.

# Cache:

Para el cache se debe tener en cuenta que es de memoria volatil, en otras palabras una vez se apage el contenedor del cache este se borrara a diferencia de la base de datos que permanece incluso apagada. Tambien se incluyeron valores especiales a el cache para su montaje de docker que pueden ser cambiados para su experimentacion:

- --policy: Este valor indica el tipo de politica que usara el cache, tiene dos opciones que son: lru y lfu.
- --size: Este valor indica que tan grande sera el cache, funciona tal que si el tamaño es de 100 esas seran 100 entradas o eventos que podra guardar.

Apartir de la entrega 2 se considera tambien que ahora el cache usa una logica simila a la de un servidor de socket tcp en un puerto al que otros servicios se conectan para interactuar con el. Fuera de eso su funcionamiento sige siendo el mismo a pesar de los cambios en la estructura interna.

# Utils:

En la carpeta de utils se encuentran scripts genericos que se usaron para la creacion de partes o archivos relacionados al proyecto pero que no son parte en si de la logica del proyecto en si. Ahora mismo se encuentra un script que cumple la funcion de transformar el contenido de la base de datos en un archivo csv que pueda ser leido luego con Apache pig.

# Apache Pig:

Para el apache pig se utilizo la ayuda de chatGPT para su elaboracion, en cuanto a su funcionamiento se usa el contenido de el archivo csv ya generado con la informacion de la base de datos y se limpia cualquier dato que este en blanco, repetido, incorrecto o irrelevante que no sea necesario y no aporte nada para un analisis posterior. Aparte del limpiado de los datos este tambien provee la logica para analizar los datos tal que si muchos datos estan agrupados en un solo sector basado en las direcciones geograficas de x e y se pueda considerar todos esos datos como un solo evento en vez de multiples, esto lleva a la creacion en base a sus multiples analisis de los outputs guardados en la carpeta de Data.

# Data:
En esta carpeta se encuentran los archivos que no proveen ninguna logica ademas de ser solo accedidos para la extraccion de su contenido. Ejemplos son el archivo csv con la data de la base de datospara el acceso de apache pig y los outputs del apache pigs que pueden ser clasificados en:

- comuna/ciudad: En primera instancia se buscada el separar datos por comunas pero debido a la naturaleza de los datos ya extraidos se procedio a considerar este dato como ciudad ya que eso es lo que los datos traian incluidos. Este dato representa las ciudades observadas y la cantidad de eventos dentro de estas.
- tipo: Aqui se incluyen los tipos de eventos que existen y cuanto de cada uno hay en total.
- tipo_comuna/ciudad: Cuantos de cada tipo de evento hay en cada ciudad.
- top_comunas/ciudades: Ciudades/comunas con mas eventos en total.
- top_tipos: Eventos mas frecuentes.
- usuarios_por_zona: Cantidad  de usuarios dentro de determinados bloques de 1 kilometro dentro de el area observada.
- zona_mas_concurrida: Zonas donde se detectaron una mayor cantidad de usuarios.


# Uso del sistema en la experiencia de los alumnos:

Se utilizo en gran medida Visual studio code y docker desktop, con visual studio se trabajo en la carpeta con los codigos y archivos y fue desde donde se fue modificando los valores, con esto en mente se hizo uso de extensiones de la aplicacion para correr automaticamente los servicios por separado cada vez que era necesario probar un nuevo valor desde el archivo docker-compose. En cuanto a la visualizacion de logs y comportamiento de los servicios ya montados se uso docker desktop ya que no se tenia una gran familiaridad con el uso de desktop desde terminal. Apartir de la entrega 2 tambien se incluyo la creacion de un docker con lo necesario para usar apache pig desde el cual se usan comandos en el docker desktop para ejecutar el archivo pig en la carpeta respectiva a este, esto con la intencion de obtener los outputs en datas para analisis. Fuera de eso el sistema sige funcionando de la misma manera siendo los dos contenedores mas usados el cache y el generador de trafico para hacer consultas a este y probar su funcionamieno en general.

  
