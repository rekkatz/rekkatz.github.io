---
title: "Colector de eventos McAfee Mvision ePO"
date: "2020-06-02"
categories: 
tags: 
media_subpath: /assets/img/posts/2020-06-02-script-colector-de-eventos-mcafee-mvision-epo-cloud
image:
   path: header/script_mvision.webp
   lqip: data:image/webp;base64,UklGRkQAAABXRUJQVlA4IDgAAACQAwCdASoUAAsAPzmGulOvKKWisAgB4CcJZQAAW+uEaDUmTEAAAP66ezUrPdzaOMM9nLrHSCwAAA==
   
published: true
---

¡Hola compañeros!

En esta entrada os quiero enseñar uno de mis primeros scripts en Python3 para extraer los eventos de la solución **McAfee Mvision ePO Cloud**.

# Colector de eventos McAfee Mvision ePO Cloud

## Descripción de Script

Trabajando como analistas o en ámbitos dedicados a blueteam,  en algunas situaciones nos vemos en la necesidad de tener que extraer los eventos de las soluciones que gestionamos y añadirlos al **SIEM** que tengamos para poder realizar la integración, correlación y generación de alertas según umbrales, etc, y de esta forma aportar mayor proactividad al entorno ante situaciones de seguridad.

En este caso, el script ha sido desarrollado para poder extraer los eventos según el cliente que configuremos, permitiéndonos configuraciones individuales de extración de eventos de la solución Cloud.

>El script se encuentra en mi Github, os lo dejo por aquí:
>
><https://github.com/rekkatz/Mvision_ePO_Collector>

Antes de empezar, hay que modificar la variable "_**self.path**_" del archivo "_**Mvision\_epo.py**_" con la ruta donde se encuentre el directorio del script.

Este script consta de varios archivos y directorios que pasaré a detallar:

- _**setup.py**_: Es el primer archivo que debemos ejecutar, ya que se encarga de configurar el cliente y crear un archivo "CFG" donde almacenará la información de este.
- _**mvision\_epo.py**_: Es el archivo que se debe ejecutar en segundo lugar, este se encarga de la autenticación y obtención del token access para poder extraer los eventos y almacenarlos en un archivo.log
- _**general.cfg**_: Este archivo contiene los ID de eventos que NO queremos extraer de la ePO de Mvision.
- _**Directorio CONF**_: En este directorio se encuentran los archivos de configuración de los clientes, creados a partir del setup.py. Se crea una vez finalizado el setup.py
- _**Archivo CONF**_: Este archivo contiene las credenciales de autenticación, el client\_ID de Mvision, marca de tiempo para control de eventos, numero de eventos extraídos hasta la fecha, etc.

## Ejecución de Setup.py

En primer lugar como he comentado, ejecutamos el archivo "setup.py" para configurar el cliente, nos irá pidiendo los datos uno a uno:

![](body/post9-image1.png)

Una vez configurado el cliente, pasamos a mostrar el archivo creado, en este caso "**_Prueba1.cfg_**":

![](body/post9-image2.png)

- **client**: Nombre de cliente configurado
- **client\_ID**: Este es el identificador de cliente, lo podemos obtener a través del siguiente enlace una vez estemos logueados: https://auth.ui.mcafee.com/support.html. Se codifica en base64.
- **epo\_user**: Usuario de acceso a Mvision (podemos crear uno de solo lectura). Se codifica en base64.
- **epo\_pass**: Contraseña de acceso. Se codifica en base64
- **epo\_scope**: Alcance de módulos para extraer eventos. Es decir, de que módulos se extraeran, por defecto se han configurado todos.
- **dir\_events**: Directorio donde se almacenarán los eventos extraídos en un archivo ".log". Unicamente se debe definir el directorio con ruta absoluta.
- **state**: Contador del cual nos permite identificar los eventos con un campo numérico (numevent).
- **last\_since**: Control de tiempo para poder extraer los eventos desde la ultima ejecución, evitando tener que extraer todos cada vez que se ejecuta.

## Ejecución de Mvision\_epo.py

Como segundo paso, se debe ejecutar el script "_**Mvision\_epo.py**_" con el argumento cliente, como se muestra en la siguiente imagen:

![](body/post9-image3.png)

Nos indica que el script se ha ejecutado correctamente y los eventos han sido recolectados.

Ahora si echamos un ojo al archivo "CFG" del cliente en cuestión, veremos que la variable state y last\_since, han sido definidas con otros valores.

## Revisión de Logs

Una vez se haya ejecutado el script anterior, pasamos a visualizar los eventos recolectados. En este caso voy a mostrar una parte de los logs, ya que no he podido crear un tenant de prueba para la solución:

![](body/post9-image4.png)

## Opcional - Automatización CRON

Como estaréis pensando, este script sería conveniente que se fuese ejecutando cada X tiempo para ir recolectandos los eventos que van sucediendo en la solución. Acordarse que en la ejecución del archivo, este debe tener el argumento "cliente" para que se ejecute con el archivo "CFG" en cuestión.

Añadimos la ejecución a CRON y de esta forma automatizamos. Unicamente nos quedaría la opción de indicarle al SIEM de donde debe leer los eventos, que en este caso sería de un archivo local.

Para finalizar, indicar como he comentado al principio que ha sido el primer script que he realizado en Python3. por lo que el código podrá ser optimizado de mejor forma, soís libres de ello.

Espero que os pueda servir de ayuda y como digo siempre, cualquier duda, sugerencia, etc, la podéis dejar en los comentarios.

Nos vemos en el próximo artículo.

Saludos!
