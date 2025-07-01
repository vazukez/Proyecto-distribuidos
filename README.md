# Proyecto-distribuidos

Proyecto semestral de el ramo sistema distribuidos realizado por Alejandro Saldías y Matias Vasquez. Editado para entrega de la parte 3 y final del proyecto.

# Distribucion de archivos

Cada carpeta del github contiene el codigo correspondiente a uno de los servicios montados en docker(con la excepcion de los utils y la data), al archivo python(pig en el caso correspondiente) con la logica de cada uno se añaden un documento txt con los requerimientos del servicio, tipo librerias necesarias a instalar, y un archivo dockerfile con las instrucciones a ejecutarse al hacer el contenedor en docker. En cuanto al archivo docker-compose.yml es el archivo usado para montar todos los servicios de forma individual bajo la misma red para que puedan comunicarse sin problemas entre si, este archivo considera solo los archivos dentro de las carpetas de cada servicio por lo que para mantener el orden y evitar errores se dejan las carpetas de cada codigo lo mas minimilistas posibles , solo con lo necesario para el montaje. El archivo docker-compose.yml tambien tiene las logicas para el sistema de almacenamiento que corresponde a una base de datos Mongo, el contenedor pig para el procesado de los datos y los contenedores correspondientes a kibana y elasticsearch. Tambien se incluyo un archivo json con todos los eventos registrados por el grupo atraves del scraper para su rapida implementacion, asi como una carpeta data con informacion importante para analisis obtenidas de apache pig y archivos csv con la info de la base de datos para la lectura del programa pig y otro para la subida del trafico generado al cache a elastic/kibana.

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

Para el scraper se reviso posibles puntos nuevos para el acceso a los datos del mapa de waze, en base a esto tambien se mejoro el area dentro de la que se tomaban los datos necesarios para el trabajo. Seguido se prescindio de los datos de eventos antiguos y se uso el scraper para la obtencion de nuevos datos capaces de cumplir con fallos que se tuvieron en entregas anteriores como el poder mostrar data de multiples comunas a la vez ypoder diferenciarlas.

# Generador de trafico:

Para el generador de trafico se modifico para que funcionara solamente con su funcion de poisson y se uso para netamente hacer pruebas del cache conectado a elastic/kibana y poder obtener estadisticas relacionadas con el porcentaje de hits o miss generados.

# Cache:

Para el cache se debe tener en cuenta que es de memoria volatil, en otras palabras una vez se apage el contenedor del cache este se borrara a diferencia de la base de datos que permanece incluso apagada. Para esta ultima entrega se genera un cache de LRU debido a su facilidad de implementación y comprensión. En el caso de esta entrega el cache esta conectado a elastic/kibana para hacer sus consultas y para hacer esto usa la libreria de requests.

# Utils:

En la carpeta de utils se encuentran scripts genericos que se usaron para la creacion de partes o archivos relacionados al proyecto pero que no son parte en si de la logica del proyecto en si. Uno de estos script cumple la funcion de transformar el contenido de la base de datos en un archivo csv que pueda ser leido luego con Apache pig y los otros scripts corresponden a scrips de python para enviar a elastic/kibana los datos de la base de datos, los outputs del pig y los registros del cache.

# Apache Pig:

Para el apache pig se utilizo la ayuda de chatGPT para su elaboracion, en cuanto a su funcionamiento se usa el contenido de el archivo csv ya generado con la informacion de la base de datos y se limpia cualquier dato que este en blanco, repetido, incorrecto o irrelevante que no sea necesario y no aporte nada para un analisis posterior. Aparte del limpiado de los datos este tambien provee la logica para analizar los datos tal que si muchos datos estan agrupados en un solo sector basado en las direcciones geograficas de x e y se pueda considerar todos esos datos como un solo evento en vez de multiples, esto lleva a la creacion en base a sus multiples analisis de los outputs guardados en la carpeta de Data. Estos outputs generalmente se separan en base a comunas y tipos donde tipos son la keyword para identificar si se trata de una alerta o usuario y las comunas para identificar el area del mapa donde se genero el evento.

# Data:
En esta carpeta se encuentran los archivos que no proveen ninguna logica ademas de ser solo accedidos para la extraccion de su contenido. Ejemplos son el archivo csv con la data de la base de datospara el acceso de apache pig y los outputs del apache pigs que pueden ser clasificados en:

- comuna: En primera instancia se buscada el separar datos por comunas pero debido a la naturaleza de los datos ya extraidos se procedio a considerar este dato como ciudad ya que eso es lo que los datos traian incluidos. Este dato representa las ciudades observadas y la cantidad de eventos dentro de estas.
- tipo: Aqui se incluyen los tipos de eventos que existen y cuanto de cada uno hay en total.
- comuna: Cuantos eventos suceden dentro de cada comuna asi como todas las comunas que hay.
- tipo_comuna: Cuantos de cada tipo de evento hay en cada comuna.
- top_comunas: Comunas con mas eventos en total.
- top_tipos: Eventos mas frecuentes.


# Uso del sistema en la experiencia de los alumnos:

Se utilizo en gran medida Visual studio code y docker desktop, con visual studio se trabajo en la carpeta con los codigos y archivos y fue desde donde se fue modificando los valores, con esto en mente se hizo uso de extensiones de la aplicacion para correr automaticamente los servicios por separado cada vez que era necesario probar un nuevo valor desde el archivo docker-compose. En cuanto a la visualizacion de logs y comportamiento de los servicios ya montados se uso docker desktop ya que no se tenia una gran familiaridad con el uso de desktop desde terminal.

- Asumiendo que ya se tenga cargada la base de datos, se procede a hacer uso del contenedor de la base de datos mongo.
- De ser requerido se puede iniciar el scraper para capturar datos y apagar una vez se tengan suficientes.
- El contenedor de pig es solo necesario usarlo en el caso de que se quieran procesar los datos de la db, en cuyo caso se debe ingresar al contenedor con un bash o a traves del docker desktop y ejecutar el archivo "procesamiento.pig"
- Los contenedores de elasticsearch y kibana si son necesarios que esten corriendo para poder acceder al localhost de kibana con elasticsearch para la visualizacion de los datos. Notar que elasticsearch tarda mas en iniciar y hasta que inicie bien kibana no se puede conectar adecuadamente por lo que hay que darles un tiempo para que esten en completo funcionamiento. Con el kibana/elasticsearch funcionando se pueden hacer uso de los scrips de la carpeta Utils para mandar los datos de la base de datos, el trafico del cache y los datos procesados por pig a kibana/elasticsearch para su visualizacion. Una vez subidos los datos se deben crear los index patterns para cada tipo de dato subido y una vez hecho eso deberia ser posible el visualizarlo todo en el discover, de esa misma manera tambien se pueden generar los graficos y mapas basados en los datos.
- Una vez montado elastic y kibana se puede iniciar el cache que en el caso de que reciba trafico generara requests al elastic. En esta parte de puede hacer uso del generador de trafico para probar el cache, notar que el generador de trafico genera dentro del contenedor su archivo csv con el log del trafico y este puede ser extraido para ser mandado a elastic pero para la facilitacion del proceso este csv ya se entrega directamente en el repositorio.

  
