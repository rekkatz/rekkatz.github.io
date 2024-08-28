---
title: "Ataque Man in the Middle en APT &lt; 1.4.9"
date: "2019-07-26"
categories: [Red-Team]
tags: [Debian,Hacking,Vulnerabilidad]
published: true
media_subpath: /assets/img/posts/2019-07-26-ataque-man-in-the-middle-en-apt-1-4-9/
image:
  path: header/bypasseados_mitm_apt.webp
  lqip: data:image/webp;base64,UklGRmIAAABXRUJQVlA4IFYAAAAQAwCdASoUAAsAPzmGulOvKKWisAgB4CcJaQAAS+y50LgA/tDvpkZWK+xyEveRL68Vf98+gtDPSCh6WuZh7x8HjR7Aq7PtpgfnuRjpKVkT7aG2ab7gAA==

---

Buenas lectores!

En esta primera entrada, quiero mostrar un tipo de ataque que se basa en Man in the Middle APT, el cual descubrí realizando una de las máquinas de la plataforma Hackthebox.

Para ponernos un poco en contexto, se trata de una vulnerabilidad en el gestor de paquetes de alto nivel en los sistemas GNU/Linux, que se encuentra en versiones inferiores a la 1.4.9 de APT, esta vulnerabilidad nos permite saltarnos el proceso de verificación de los paquetes que son solicitados para actualizarse o instalarse.

La vulnerabilidad en cuestión se trata de: <https://security-tracker.debian.org/tracker/CVE-2019-3462> , esta nos permite redireccionar las peticiones de APT a un servidor atacante en el cual podremos gestionar los paquetes que tratará de solicitar la máquina vulnerable al ejecutar "**apt-get update && apt-get upgrade**", estos paquetes estarán manipulados aumentado su versión y añadiendo en los scripts de instalación el código de la shell inversa.

Como veréis a continuación, he intentado replicar el escenario que me encontré al realizar el CTF, sinceramente me gustó la manera de manipular paquetes Debian el cual me trajo bastante dolor de cabeza, hasta que al final se obtiene la querida inverse shell root y el dolor se convierte en satisfacción.

**Punto importante a comentar**: este tipo de ataque se realiza una vez se ha obtenido usuario en la máquina vulnerable y nos disponemos a realizar Privesc (escalada de privilegios).

Sin más dilación, vamos allá:

Direcciones IP:

- Kali Linux: _192.168.17.142_
- Debian Server 7.10: _192.168.17.143_

Lo primero que me encontré fue que el user obtenido, poseía permisos de **SUDO NOPASSWD** para "**apt-get update && apt-get upgrade**" y permisos para poder cambiar redirecciones de tráfico "ftp\_proxy, http\_proxy y https\_proxy", a partir de aquí empieza la diversión.

Realizamos redirección sobre la variable "http\_proxy" hacia nuestra máquina y puerto:

![Modificación de variable http_proxy](body/Post2_Imagen1.jpg)
_Modificación de variable "http\_proxy"_

Podemos comprobar que funciona ejecutando un servidor web temporal con PHP y ejecutar el comando "sudo apt-get update" en la máquina vulnerable.

![Prueba de conexiones entrantes al servidor web temporal](body/Post2_Imagen2.jpg)
_Prueba de conexiones entrantes al servidor web temporal_
  
[//]: <> (This may be the most platform independent comment)

Como vemos, al no encontrar archivos de los cuales realizar llamada, nos muestra error 404 en todas las peticiones.

Como ya tenemos la redirección aplicada en la variable de entorno, lo siguiente que se me pasó por la cabeza fue...si tengo que "engañar" al servidor para que actualice un paquete manipulado, tendré que tener un paquete real ¿no?.

Listamos los paquetes que tiene el servidor y elegimos uno, en este caso elegí el paquete "tar" y mostramos detalles del paquete instalado en el servidor:


![Búsqueda del paquete "tar"](body/Post2_Imagen3.jpg)
_Búsqueda del paquete "tar"_


Creamos los directorios temporales donde estará nuestro pequeño repositorio y descargamos el paquete "**tar**" del repositorio oficial.


![Creación de directorios y descarga de paquete "tar" original](body/Post2_Imagen4.jpg)
_Creación de directorios y descarga de paquete "tar" original_


Una vez tengamos el paquete ya en nuestra posesión, vamos a desempaquetarlo para poder listar y manipular:


![Desempaquetado de archivo .deb descargado](body/Post2_Imagen5.jpg)
_Desempaquetado de archivo .deb descargado_


El primer archivo que tendremos que modificar será "**control**", este archivo lleva como su propip nombre indica un control sobre el paquete que lo contiene: versión, arquitectura, paquete, paquetes sugeridos, etc. A nosotros nos interesa modificar la versión del paquete para aumentarla y que el servidor vulnerable crea que hay una versión más reciente de este y por consiguiente que realice la petición para actualizar e instalar.

![Archivo control sin modificar versión](body/Post2_Imagen6.jpg)
_Archivo control sin modificar versión_

![Archivo control con versión modificada](body/Post2_Imagen7.jpg)
_Archivo control con versión modificada_


En este punto vamos a realizar un pequeño inciso. Cuando tenemos que manipular paquetes de tipo .deb y añadir nuestro pequeño código para la shell inversa, nos tenemos que centrar en 2 tipos de scripts que contienen estos paquetes (puede contenerlo si lo requiere o no), los cuales son: "**_preinst_** y **_postinst_**".

- **PREINST:** Este script se ejecuta antes de que el paquete al que pertenece se descomprima.
- **POSTINST:** Este script se ejecuta después de la instalación del paquete.

Una vez entendido esto, vamos a modificar el archivo "**_postinst_**" para añadir nuestra shell-inversa. En el caso de que hayáis elegido un paquete que no contenga un archivo de "preinst" o "postinst", se puede crear manualmente y otorgarle permisos de ejecución (755).


![Cambiar tipo de shell a utilizar (bash) y añadir código de reverse shell](body/Post2_Imagen8.jpg)
_Cambiar tipo de shell a utilizar (bash) y añadir código de reverse shell_

Cuando ya tenemos manipulado el paquete,  volvemos a empaquetar y aumentar la versión en el nombre:

**Importante:** la versión del paquete DPKG en la máquina de Kali y en Debian, son distintas, por lo tanto pueden surgir problemas a la hora de intentar desempaquetar al realizar "upgrade" y que no reconozca el formato de compresión (gz y xz) o permisos con los cuales se ha empaquetado, por eso tenemos que engañar el empaquetado con _fakeroot_.

- **fakeroot:** ejecuta una orden en un entorno que falsea privilegios de superusuario para la manipulación de ficheros <https://wiki.debian.org/FakeRoot>

![Empaquetado con fakeroot](body/Post2_Imagen9.jpg)
_Empaquetado con fakeroot_

Una vez empaquetado, podemos eliminar el directorio "modif\_tar" y el paquete tar con la versión anterior.

Otro de los archivos importantes a la hora de realizar una actualización a través de APT, es el archivo "**_Packages_**", este contiene la ruta de donde se encuentra el paquete a instalar y los hashes (_md5, sha1, sha256 y sha512_), los cuales verifican que ningún archivo ha sido manipulado...o si =P.

Es importante obtener los hashes del paquete manipulado, para ello utilizamos las herramientas de generación de hashes de Kali:

![Obtención de Hashes para paquete "deb" manipulado.](body/Post2_Imagen10.jpg)
_Obtención de Hashes para paquete "deb" manipulado_

Podemos crear el archivo y almacenar la salida que hemos obtenido en uno de los pasos anteriores con el comando de "apt-cache show tar", recordar añadir los checksum del paso anterior, cambiar la versión y el tamaño del paquete .deb, si no muestra como he comentado en el paso anterior los campos de **_Filename_** (Ubicación del archivo a instalar), _**Size**_ (tamaño del archivo a instalar) y _**Hashes**_, lo podemos introducir manualmente:

![Creación de archivo "Packages"](body/Post2_Imagen11.jpg)
_Creación de archivo "Packages"_

Comprimimos el archivo Packages y también tenemos que obtener los hashes de estos dos archivos... sé lo que estás pensando, pesado no? Al final obtendremos la recompensa 😜

![Obtención de Hashes de archivos "Packages" y "Packages.gz"](body/Post2_Imagen12.jpg)f
_Obtención de Hashes de archivos "Packages" y "Packages.gz"_

En este punto, tendremos que crear otro archivo más, que es el "_**Release**_"... no desesperes! Este archivo contiene la información y ubicación los archivos "_**Packages**_" y "_**Packages.gz**_", así como sus hashes y tamaño de estos. 

Importante que la V_ersión del servidor Debian, Arquitectura, Tamaño y Hashes_ sean los correctos.

![Creación de archivo "Release"](body/Post2_Imagen13.jpg)
_Creación de archivo "Release"_

Hasta el momento, nuestro pequeño repositorio contendrá estos archivos:

![Listado de archivos hasta el momento](body/Post2_Imagen14.jpg)
_Listado de archivos hasta el momento_

Como estáis pensando y si no, ya lo digo yo, los archivos creados no están en sus ubicaciones correctas, así que tendremos que crear las rutas de los directorios temporales del repositorio, en las cuales tendrá que buscar la máquina vulnerable al realizar la petición a través de APT. 

Los directorios temporales, se han dejado por defecto, pero en los archivos de _Release y Packages_, podemos indicarle directorios distintos para que sea más llevadero. 

Nos podemos basar en las peticiones que ha realizado la máquina Debian al ejecutar el comando `apt-get update` y que hemos podido observar en nuestro servidor web temporal.

Las peticiones estaban realizando la solicitud de los archivos creados pero en rutas distintas, estas rutas serán las que tendremos que crear:

- http://192.168.17.142/dists/wheezy/Release
- http://192.168.17.142/dists/wheezy/main/binary-amd64/Packages
- http://192.168.17.142/dists/wheezy/main/binary-amd64/Packages.gz
- http://192.168.17.142/pool/main/t/tar/tar\_1.27+dfsg-0.1\_amd64.deb

Dejo por aquí un esquema que he creado para que se entienda mejor:

![Esquema de directorios](body/Post2_Imagen15.png)
_Esquema de directorios_

Y pasamos a crear los directorios con sus rutas correctas y mover los archivos:

![Creamos directorios y nos movemos a carpeta "debian"](body/Post2_Imagen16.jpg)
_Creamos directorios y nos movemos a carpeta "debian"_

Ya tenemos todo lo necesario, ahora nos falta lo más importante:

- Ejecutamos servidor Web con PHP por si no lo hemos dejado ejecutándose en la carpeta padre, que es "debian":
    - `php -S 0.0.0.0:666`

- Ejecutamos netcat para escuchar la conexión inversa de la máquina Debian, acordarse el puerto que hemos indicado al añadir el código de la shell en el archivo "**_Postinst_**" (9999):
    - `nc -lvnp 9999`

- Ejecutar `sudo apt-get update && sudo apt-get upgrade` en la máquina Debian y cuando nos indique si estamos de acuerdo en saltar la verificación/autenticación...presionamos "Y"

Solicitudes y los códigos 200 del servidor web temporal:

![Solicitudes entrantes](body/Post2_Imagen17.jpg)
_Solicitudes entrantes_

Como opinión personal, es cierto que se tienen que dar algunas coincidencias para poder realizar este tipo de ataque, pero sabemos que existen usuarios que no tienen permisos 100% y a estos se le otorgan permisos "mínimos" para llevar a cabo ciertas acciones en los sistemas que administran. 

También conocemos compañeros, amigos, familiares, etc, que siguen obcecados con versiones anteriores de alguna distribución por su sencillez o simplemente por que es la versión de distribución que mejor conoce.

Recordar actualizar el paquete APT a la última versión para corregir de este tipo de vulnerabilidades.

Nos vemos en el próximo artículo.

Saludos!
