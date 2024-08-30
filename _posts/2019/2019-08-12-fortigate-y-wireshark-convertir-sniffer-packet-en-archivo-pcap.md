---
title: "Fortigate y Wireshark - Convertir Sniffer Packet en archivo PCAP"
date: "2019-08-12"
categories: [Fortigate, Tools]
tags: [Fortigate, PCAP, Sniffer-Packet, WireShark]
media_subpath: /assets/img/posts/2019-08-12-fortigate-y-wireshark-convertir-sniffer-packet-en-archivo-pcap
image:
   path: header/convert_fortigate_wireshark.webp
   lqip: data:image/webp;base64,UklGRlwAAABXRUJQVlA4IFAAAAAwAwCdASoUAAsAPzmEuVOvKKWisAgB4CcJQAAKjHtBnFPQAP7ZWOGIG5+aZAMPEF0wrOLgQlCQHWVS6q2Gbh64qS/PngHGeVubWOXTKIRQAA==
   
published: true
---

¡Buenas lectores!

En esta entrada quiero compartir una de las herramientas de conversión de tráfico para _**Fortigate**_ que he utilizado en varias ocaciones durante mi día a día para obtener un archivo PCAP durante un análisis de tráfico, en el caso de no tener la opción de "_Packet Capture_" en el dispositivo Fortigate.

Para ello utilizaremos los siguientes Scripts/Herramientas:

- [Fgt2eth.exe](https://github.com/rekkatz/fortigatetools/raw/master/fgt2eth.exe) (Windows)
- [Fgt2eth.pl](https://github.com/rekkatz/fortigatetools/blob/master/fgt2eth.pl) (GNU/Linux)[](https://github.com/rekkatz/fortigatetools/blob/master/fgt2eth.pl)

En algunos casos, es posible que esta opción no aparezca en el dispositvo,  ya sea por que tiene una versión inferior a la 6.0, por que no tiene disco físico el appliance o porque el modelo de este no trae la opción de fábrica.

Para la utilización de esta herramienta, necesitaremos conocer por encima la herramienta de diagnóstico "_**sniffer packet**_" que trae por CLI los dispositivos de la marca Fortinet en sus sistemas _**FortiOS**_.

En resumidas cuentas, lo que haremos será obtener mediante CLI las tramas de conexiones generadas y utilizar la herramienta "**_fgt2eth_**" para la conversión de un archivo TXT a un archivo PCAP para posteriormente ejecutarlo con _**Wireshark**_.

Requisitos que tendremos que tener en nuestra máquina:

- [ActivePerl](https://www.activestate.com/products/activeperl/downloads/) (En el caso de Windows)
- [Wireshark](https://www.wireshark.org/download.html)
- [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) o [MobaXterm](https://mobaxterm.mobatek.net/download-home-edition.html)

Vamos al lío:

Para empezar utilizaremos Putty donde tendremos que configurar la opción "**_All session output_**" para que almacene en un archivo LOG todo el output de la sesión SSH que vamos a utilizar:

![_Configuración PUTTY_](body/post3-image1-1.jpg)
_Configuración PUTTY_

Una vez tengamos la opción indicada marcada y la ubicación donde se almacenará el archivo, establecemos conexión SSH con el dispositivo Fortigate.

Ahora que estamos dentro, vamos a ver que es la herramienta de "**_Sniffer Packet_**".

Esta herramienta nos permite realizar un rastreo o Sniffer del tráfico de una interfaz específica o varias interfaces a la vez, muy muy parecido a la ejecución de tcpdump pero integrado en FortiOS.

Su sintaxis es la siguiente:

```powershell
diagnose sniffer packet <interface> <'filter'> <verbose> <count> a
```

Y las opciones que nos permite utilizar esta herramienta son:

- _**Interface**_: Es la interfaz por la cual se capturará el tráfico, podemos especificar "any" y capturará por cualquier interfaz que esté configurada.
- _**Filter**_: Será el filtro que le indiquemos para que realice match del tráfico deseado. Puede contener la siguiente sintaxis:  `[[src|dst] host] [[src|dst] host] [[arp|ip|gre|esp|udp|tcp] [port_no]] [[arp|ip|gre|esp|udp|tcp] [port_no]]`
- _**Verbose**_: Es el tipo de información que mostrará según las tramas capturadas, se establecen en 6 niveles de verbosidad, de menor a mayor en cuanto a detalle:
    - **Nivel 1**: Muestra la cabecera de los paquetes
    - **Nivel 2**: Muestra la cabecera y los datos IP de los paquetes
    - **Nivel 3**: Muestra la cabecera y los datos ethernet de los paquetes
    - **Nivel 4**: Muestra la cabecera de los paquetes con el nombre de interfaz
    - **Nivel 5**: Muestra la cabecera y los datos IP de los paquetes con el nombre de interfaz
    - **Nivel 6**: Muestra la cabecera y los datos ethernet de los paquetes con el nombre de interfaz
- _**Count**_: Con esta opción, podemos indicar los paquetes a recoger antes de que se detenga la herramienta. Si no indicamos nada o establecemos "0", seguirá recogiendo paquetes hasta que presionemos Ctrl + C.
- _**Opción "A**"_: Nos permite visualizar las marcas de timestamps durante la captura de las tramas.

Una vez entendido esto, vamos a lanzar la herramienta de "_**Sniffer Packet**_" en la conexión SSH que tenemos abierta al dipositivo Fortigate por CLI. Para nuestro caso, utilizaremos la opción de **Verbose 6**, para que nos muestre lo más detallado posible los paquetes capturados:

![Output de ejecución](body/post3-image2-2.jpg)
_Output de ejecución_

Como se puede ver en la imagen anterior, se ha capturado el tráfico con destino la IP de los DNS primarios de Google (8.8.8.8) a través de ICMP (Ping).

Ahora ya tendremos en el archivo LOG la salida de la sesión con Putty. Pero antes necesitamos **eliminar** la primera línea que se genera en el archivo LOG:

```powershell
=~=~=~=~=~=~=~=~=~=~=~= PuTTY log 2019.08.12 16:01:29 =~=~=~=~=~=~=~=~=~=~=~=
```

y guardamos los cambios.

En este punto llega el turno de la herramienta "_**fgt2eth.exe**_", la cual nos permitirá convertir el archivo LOG en un PCAP.

Las opciones que nos muestra la herramienta:

```powershell
Version : Dec 19 2014
Usage : fgt2eth.pl -in <input_file_name>

Mandatory argument are :
    -in <input_file>      Specify the file to convert (FGT verbose 3 text file)

Optional arguments are :
    -help                 Display help only
    -version              Display script version and date
    -out <output_file>    Specify the output file (Ethereal readable)
    
By default <input_file>.pcap is used
    - will start wireshark for realtime follow-up

    -lines <lines>        Only convert the first <lines> lines
    -demux                Create one pcap file per interface (verbose 6only)
    -debug                Turns on debug mode
```

En nuestro caso, vamos a utilizar el comando con la sintaxis:

```powershell
 fgt2eth.exe -in putty.log -out google_icmp.pcap
```

Una vez ejecutado, obtendremos nuestro archivo PCAP:

![Resultado archivo PCAP](body/post3-image3-2.jpg)
_Resultado archivo PCAP_

Ya solo nos faltaría ejecutarlo con Wireshark y comprobar que los paquetes y el tráfico recogido es el correcto:

![Resultado final](body/post3-image4-1.jpg)
_Resultado final_

Y bueno hasta aquí sería todo. Espero que os sea útil.

Comentar un par de puntos por si a alguien le salta la duda:

- En Sistemas GNU/Linux es exactamente igual, solo que hay que descargar la herramienta con extensión Perl.
- Es posible realizar Copy&Paste de la salida en pantalla que nos muestra la consola CLI directamente desde la Webgui y pegarla en un archivo TXT y pasarle el conversor.
- En las versiones 6.0 y superiores de FortiOS, han implementado la opción de "Packet capture" independientemente de si tiene disco físico o no, pero por si acaso, siempre viene bien tener esta herramienta.
- En esta entrada se ha utilizado el Visor de tráfico _**Wireshark**_, pero se puede utilizar cualquier otro como _**NetworkMiner**_.
- Referencias para "_**Sniffer Packet**_":  
    - [https://kb.fortinet.com/kb/documentLink.do?externalID=11186](https://kb.fortinet.com/kb/documentLink.do?externalID=11186), también podéis descargar las herramientas en el píe de página del enlace anterior.

Cualquier duda o sugerencia, podéis dejarla en la caja de comentarios.

Nos vemos en el próximo artículo.

Saludos!
