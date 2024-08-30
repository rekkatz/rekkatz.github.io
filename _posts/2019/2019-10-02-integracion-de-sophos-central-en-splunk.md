---
title: "Integración de Sophos Central en Splunk"
date: "2019-10-02"
categories: 
tags: 
media_subpath: /assets/img/posts/2019-10-02-integracion-de-sophos-central-en-splunk
image:
   path: header/portada_integracion_sophos_splunk.webp
   lqip: data:image/webp;base64,UklGRmIAAABXRUJQVlA4IFYAAACQAwCdASoUAAsAPzmIulQvKSWjMAgB4CcJYwAAVFG0Ig/97vgAAP7ZXJPYtQkV5TwF42BFHecBuRFUxsOJZ+gPMHvzb4+TSU1nf/VTQxui1wOHKoAAAA==
   
published: true
---

Después de 1 mes y medio alejado de las redes por vacaciones, trabajo y demás, volvemos con un artículo que a más de uno le pueda servir de ayuda sobre todo en la parte de BlueTeam e Integración. Vamos a ver como realizar la integración de **_Sophos Central_** con un SIEM, en este caso el SIEM que voy a utilizar y el cual tengo montado para uso personal es **_SPLUNK_**.

## Descripción

En este artículo, veremos como se integra a través de un script que podemos descargar desde Github. Como alguno sabrá, también es posible integrar **_Sophos Central en Splunk_** a través de un TA, el problema que tenemos a la hora de hacerlo de esta manera es que solo permite 1 API por TA y si tenemos varios clientes, no nos sirve ya que son varias API para un único TA.

He de comentar que en principio no importa que tipo de SIEM estemos utilizando, siempre y cuando este pueda recoger inputs locales o recibirlos a través de SYSLOG. Para este caso se va a realizar recogiendo un archivo local y añadiéndolo al SIEM para su monitorización.

## Requisitos

Para la integración de _**Sophos Central**_ con nuestra solución SIEM, necesitaremos descargar desde _Github_ el script que nos permite realizar la llamada a la “_API + Headers_”, para así extraer las alertas y eventos que se produzcan en la consola de **_Sophos Central_**.

- Descarga del Script: <https://github.com/sophos/Sophos-Central-SIEM-Integration>

Descargamos el script, en mi caso lo he ubicado dentro del directorio _**"etc"**_ en el directorio home de Splunk: **_/opt/splunk/etc/Sophos-Central-SIEM/_**

![](body/post4-image1.png)

Output de help del binario "**_siem.py_**" :

![](body/post4-image2.jpg)

El archivo que tendremos que modificar para añadir la API es "**config.ini**", lo veremos en pasos siguientes.

## Generación de API en Sophos Central

Pasamos a **_Sophos Central_** para generar la API. Os dejo las imágenes para que sea más visual:

Nos dirigimos a **_"Configuración global"_** -> **_"Administración de token de API"_**:

![](body/post4-image3.png)

Presionamos en la esquina superior derecha en "_**Añadir Token**_", establecemos un nombre para nuestra API Token y guardamos:

![](body/post4-image4.jpg)

Nos apareceran directamente las API's generadas, para este caso nos interesa "_URL acceso API + Encabezados_", la copiamos directamente del botón en el lateral de esta:

![](body/post4-image5.png)

## Modificación de Script y añadir API

Una vez generada y copiada la API que necesitaremos, tendremos que dirigirnos al directorio que hemos descargado desde Github y editar el archivo de configuración "**config.ini**", pegaremos la API en la 4ª línea que comienza con "**token\_info**":

![](body/post4-image6.jpg)

Podemos elegir el formato de salida que tendrán los eventos generados **(**_**json, cef** o **keyvalue**_), el nombre del archivo output txt que los contendrá, nos permite elegir si queremos eventos, alertas o todo (_**event, alert** o **all**_) y por último nos permite configurar las propiedades para un reenvío a través de Syslog, el cual no utilizaremos en este caso.

Una vez añadida la API, procedemos a ejecutar el archivo "_**siem.py**_" y obtendremos el archivo con el nombre indicado anteriormente en la ubicación "**./log/_ARCHIVO_.txt**"

Podemos visualizar el archivo output generado:

![](body/post4-image7.jpg)

He de comentar que cuando ejecutamos "**_siem.py_**", extraerá únicamente los eventos/alertas nuevos que no han sido generados anteriormente como máximo en 24 horas, en su ejecución inicial únicamente recupera las últimas 12 horas ya que no tenemos generado el archivo de estado. A través de los comandos en la ejecución del binario, podemos indicarle que en su ejecución inicial, recoja las últimas 24 horas (_\-s SINCE o --since=SINCE_). 

En la carpeta "**_state_**", se almacena el estado en el cual quedó en la última ejecución para que así no se duplique la extracción de eventos/alertas en el archivo output.

![](body/post4-image8.png)

Bien, ya tenemos el archivo de configuración **_"config.ini"_** con la API añadida y se ha realizado la primera ejecución de **_"siem.py"_**, solo nos faltaría automatizar el proceso para ejecutar el binario **_"siem.py"_** cada X tiempo para que las alertas y eventos se vayan agregando automáticamente al archivo de salida txt.

Tengo que comentar que tuve problemas a la hora de automatizar la ejecución del binario, si lo añadía directamente con "_crontab -e_", no se ejecutaba correctamente. Al final decidí crear un script en bash (por llamarlo de alguna forma) que contuviese el cambio de directorio a la ubicación del binario y la ejecución y en el **archivo crontab** alojado en **/etc** añadir el comando para que se ejecute cada X tiempo.

Existe la posibilidad de realizar la automatización desde el propio Splunk añadiendo Scripts y tiempo de ejecución, pero creo que es mejor que estos procesos se lleven a cabo fuera de la solución Siem, ya que le estaríamos añadiendo un consumo extra. 

De todas formas si alguien conoce otra alternativa para realizar este proceso, que lo deje en los comentarios y estaré agradecido de poder leerlo y añadirlo a la lista =P

Vamos al lío, creamos el script en bash:

![](body/post4-image9.jpg)

Le asignamos **permisos de ejecución** y nos dirijimos a **/etc** para editar el archivo **crontab** directamente con el editor, añadimos la última línea que nos permitirá automatizar el proceso de ejecución.

Como se puede ver en la imagen, está puesto para que se ejecute cada 1 min ya que estuve realizando comprobaciones por el tema del script y demás, pero podéis indicarle el tiempo que consideréis necesario:

![](body/post4-image10.jpg)

Una vez modificado y los cambios guardados en el archivo _**crontab**_, comprobamos en _**"/var/log/syslog"**_ que se está ejecutando correctamente:

![](body/post4-image11.jpg)

Como podemos ver en la imagen anterior, el proceso se ejecuta cada minuto, bien hemos terminado la primera parte, pasemos a la segunda parte que tiene que ver con Splunk y como añadir Inputs Locales.

## Agregando Local Input en Splunk

Nos dirigimos a Splunk y hacemos clic en **_"Settings"_** > **_"Data Inputs"_**:

![](body/post4-image12.jpg)

Tenemos que añadir un nuevo Local Input de tipo _Files & Directories_. Hacemos clic en _**"+ Add new"**_:

![](body/post4-image13.jpg)

Nos abrirá la ventana para configurar y seleccionar el archivo local.

Seleccionamos **Continuously Monitor** para que constantemente esté comprobando el contenido del archivo e indexarlo, hacemos clic en **Browse** y seleccionamos el archivo que vamos a monitorizar, en este caso el archivo output txt que genera el binario _**siem.py.**_

![](body/post4-image14.jpg)

![](body/post4-image15.jpg)

Una vez realizado, continuamos pulsando en **Next** en la parte superior.

Como vemos, se muestran los eventos/alertas generados en formato JSON. Podemos elegir un "Source Type" para identificar estos eventos según origen:

![](body/post4-image16.jpg)

Configuramos el Source Type para identificar al cliente y pulsamos nuevamente en **Next**:

![](body/post4-image17.jpg)

Ahora toca el turno de seleccionar el tipo de App Context - _**Search & Reporting (Search)**_  y  crear el Index (_**Índice**_) para agrupar todos los eventos, esto nos permitirá tener en un mismo saco todos los eventos y alertas de Sophos, hacemos clic en **Create a new index** y lo creamos.

Cuando se nos abra la ventana para crear el Index, únicamente introducimos un nombre para este, el resto se deja por defecto. Pulsamos en **Next**:

![](body/post4-image18.jpg)

En la siguiente ventana, nos mostrará un pequeño resúmen del Local Input a crear:

![](body/post4-image19.jpg)

Para finalizar pulsamos en _**Submit**_ y en la siguiente ventana presionamos en _**Start Searching**_ para empezar a realizar búsquedas en Splunk:

![](body/post4-image20.jpg)

Recordemos que el tipo de lenguaje que utiliza Splunk para la búsqueda y creación de queries, se denomina SPL (_Search Processing Language_), para todos aquellos que no lo sepan, es un tipo de lenguaje que combina las mejores capacidades de SQL con la sintaxis de tuberías de Unix.

## Resultado de búsqueda y tabla

Para comprobar que el archivo monitorizado está siendo indexado correctamente, podemos realizar una consulta simple utilizando el nombre del Index que hemos definido y podremos comprobar como se nos muestran correctamente los eventos:

![](body/post4-image21.jpg)

Ya para terminar, si nos queremos cercioar que efectivamente se está realizando la llamada a la API y recogiendo los eventos/alertas correctamente y de esta forma Splunk los va indexando, podemos generar una alerta en un Endpoint para que se genere una alerta en Sophos Central.

Yo he generado un par de alertas y he sacado una tabla para que se muestre de una forma más visual:

![](body/post4-image22.jpg)

### Resumen de campos JSON

- **customer\_id**: _Identificador único del cliente_.
- **datastream**: _Tipo log (alerta o evento)._
- **dhost**_: Nombre de la estación_ 
- **endpoint\_id**: _Identificador único del endpoint de la estación de trabajo._
- **endpoint\_type**: _Tipo de estación Endpoint._
- **group**: _Tipo de política en Sophos Central._
- **id**: _Identificador del evento/alerta generado._
- **name**: _Pequeño resumen de evento/alerta._
- **rt**: _Fecha/Hora de cuando se ha generado el evento/alerta._
- **severity**: _Nivel de criticidad/severidad._
- **source\_info**: _Si hacemos clic en el desplegable, nos mostrará la dirección IP de la estación de trabajo donde está instalado el Endpoint de Sophos._
- **suser**: _Nombre de usuario que ha generado el evento/alerta._


>Documentación sobre Event Types Sophos API (<https://community.sophos.com/kb/en-us/132727>)
{: .prompt-info }

## Finalizando

Es posible que os estéis preguntando...¿Y como se añaden más clientes? Bueno, para añadir más clientes lo único que hay que realizar es copiar el directorio del script y duplicarlo, acordándose de añadir la API correspondiente en el archivo de configuración, añadirlo a crontab y al script creado en bash, a parte de añadir el Local Input en Splunk con un nuevo Source Type para identificar a este cliente. El Index puede ser el mismo para todos y así tenerlos todos los clientes indexados en uno.

También cabe la posibilidad de con un mismo Script, manejar diferentes API's, pero sinceramente no lo he probado, si alguno quiere dejarme en los comentarios una forma alternativa con la que se pueda realizar, estaré encantado de leerte y aprender =D

Nos vemos en el próximo artículo.

Saludos!
