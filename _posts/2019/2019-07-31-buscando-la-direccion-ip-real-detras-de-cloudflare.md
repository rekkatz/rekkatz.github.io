---
title: "Buscando la dirección IP real detrás de Cloudflare"
date: "2019-07-31"
categories: [Hacking]
tags: [Auditoria, Censys, Cloudflare, Red-Team, Netcraft]
published: true
media_subpath: /assets/img/posts/2019-07-31-buscando-la-direccion-ip-real-detras-de-cloudflare/
image: 
 path: header/entrada_cloudflare.webp
 lqip: data:image/webp;base64,UklGRoQAAABXRUJQVlA4WAoAAAAQAAAAEwAACgAAQUxQSBkAAAABD0CQbePPvO3XiIg4EAsmO/O3ziCi/0EXAFZQOCBEAAAAsAMAnQEqFAALAD85jL5VLymmozAIAeAnCUAAC72BfG1d6/8n4AAA/p/Rfw+ps7r+wejCcA0d52K5lpXAoeujqD0hwAA=
---

¡Buenas lectores!

En esta entrada os quiero hablar sobre cómo encontrar la IP real del servidor detrás de Cloudflare.

Cuando se realiza una auditoria denominada Black Box o Caja Negra, la información que se nos proporciona para poder llevar a cabo esta, es mínima, es por eso que tenemos que desplegar nuestro arsenal de herramientas para poder encontrar información útil que nos pueda servir para realizar el Pentest.

En este caso, la dirección IP real utilizando la primera etapa de la auditoría o pentest “Footprinting”.

Para ponernos en contexto, vamos a comentar de forma resumida que es Cloudflare.

## ¿Qué es y cómo actúa Cloudflare?

Cloudflare es un servicio que realiza la labor de intermediario entre los sitios web en línea y los usuarios finales o visitantes que intenten acceder a estos sitios web. Esto permite la protección ante ataques web, protección ante ataques DDoS, protección frente a inyección de código, protección perimetral, etc.

Para entendernos, cuando un usuario intenta acceder a un sitio web, la solicitud no llega directamente al servidor web donde está alojado el sitio web, si no que intervienen los CDN de Cloudflare, que no son más que servidores DNS y Proxy Inverso los que reenvían el tráfico al servidor donde esté alojado el sitio web.

De esta manera, la dirección IP que se muestra no es la auténtica del servidor web, si no la de los servidores intermediarios.

Cloudflare permite proteger el sitio web mediante transferencia de los DNS originales del sitio, al DNS asignado por el servicio de Cloudflare.

![Esquema de funcionamiento Cloudflare](body/post3-image1.png)
_Esquema de funcionamiento Cloudflare_

## ¿Cómo saber si está detrás de Cloudflare?

Bueno, pero ¿cómo sabemos si realmente este servidor se encuentra detrás de la red de Cloudflare?

Una forma rápida sería con la ejecución de Ping al sitio web a auditar y acceder a la dirección IP que nos resuelve:

![Ejecución de ping al sitio web a auditar](body/post3-image2.jpg)
_Ejecución de ping al sitio web a auditar_

Como se puede observar al intentar acceder, nos devuelve código de Error 1003 de Cloudflare:

![Error 1003 de Cloudflare al intentar acceder a la dirección IP_](body/post3-image3.jpg)
_Error 1003 de Cloudflare al intentar acceder a la dirección IP_

Otra de las formas sería a través de herramientas web [Checkforcloudflare](https://checkforcloudflare.selesti.com/), esta nos indica visualmente si pertenece el sitio web está utilizando Cloudflare o no:

## Buscando la dirección IP real

Para buscar la dirección IP que se esconde detrás de Cloudflare, tenemos varias posibilidades que mostraré a continuación, en este caso mostraré la forma manual y en proximas entradas me centraré en herramientas automatizadas.

### Certificados SSL

Si queremos obtener datos relacionados con los certificados que se encuentran en sitios web en línea, no podemos hablar de otra herramienta mejor que [Censys](https://censys.io/), esta nos permite comprobar todos los certificados que se encuentran en Internet gracias a su base de datos, a parte también nos proporciona otros datos de interés relacionados.

Censys nos permite realizar búsquedas con operadores lógicos Booleanos, de esta forma podemos relacionar campos de una manera sencilla. ([Uso de Queries Censys](https://censys.io/ipv4/help))

Una vez estemos en la web de [Censys](https://censys.io/), seleccionaremos en la barra de búsqueda “**Certificates**”.

Para realizar una búsqueda correcta, añadiremos la siguiente query:

- Certificados para el sitio a auditar:

    - _parsed.names: “Dominio”_

- Solo mostrar certificados válidos:

    - _tags.raw: trusted_

Si esto lo juntamos con lógica booleana, nos devolverá los resultados que tengan el dominio indicado y un certificado válido:

- _parsed.names: “dominio” and tags.raw: trusted_

![Resultado de búsqueda en Censys](body/post3-image4.jpg)
_Resultado de búsqueda en Censys_

Una vez que nos ha devuelto resultado, tendremos que entrar en cada uno de estos y seleccionar "**_Explore_**" en la esquina superior derecha y a su vez en "_**IPv4 Hosts**_".

De esta forma, se realizará la búsqueda de direcciones IPv4 a través del hash-256 del certificado.

![Información de Sitio Web en Censys](body/post3-image5.jpg)
_Información de Sitio Web en Censys_

![Obtención de IP real a través de Censys](body/post3-image5-1.jpg)
_Obtención de IP real a través de Censys_

Podría ser la IP real del servidor, podemos probar a navegar directamente con la dirección IP y comprobar que nos muestra ¿redirige al sitio web? ¿muestra el sitio web correctamente con la dirección IP?

### Sitio Web y Cabeceras de correo

Aunque no lo creas, desde el propio sitio web del que queremos obtener la dirección IP, podemos obtener mucha información.

Si tenemos la oportunidad de inicializar el envío de un correo electrónico desde la página web (confirmación de registro, pedidos, suscripciones, tickets de soporte, contraseña olvidada, etc) hasta nuestro correo, existe la posibilidad de poder extraer la dirección IP real del servidor.

Para que la dirección IP sea correcta, hay que tener en cuenta que el servidor de correo de origen debe ser interno, es decir, que salga con la misma dirección IP que el sitio web, en el caso que sea un servidor de terceros o esté montado sobre otro servidor con otra dirección IP, no va a ser exactamente la dirección que buscamos... aunque nunca viene mal tenerlas para más investigación.

En el caso de la imagen siguiente, las direcciones IP son del mismo rango pero no exactamente la que quería, con lo cual tuve que subir/bajar el último octeto para conseguir la dirección IP real del sitio web.

![Cabecera de correo con direcciones IP](body/post3-image6-1.jpg)
_Cabecera de correo con direcciones IP_

Es posible que a la hora de intentar acceder a dichas direcciones IP con la barra de direcciones del navegador no podamos acceder.

Este método es posible que no funcione porque el servidor web estará configurado para ignorar las solicitudes que no contienen el nombre del host correspondiente o porque varios sitios están alojados en el mismo sitio web.

Podemos evadirlo con la herramienta CURL, esta nos permite enviar solicitudes con un encabezado personalizado con la opción "**–H**":

```bash
curl -H "Host: HOSTNAME" http://X.X.X.X
```

Si queremos conectar a través HTTPS, tendremos que agregar la opción "**\-k**" antes de la dirección IP, esta opción nos permite saltarnos el certificado.

```bash
curl -H "Host: HOSTNAME" -k https://X.X.X.X
```

Comprobaremos el código fuente HTML que nos devuelve y quien sabe, igual obtenemos algo más interesante…

Un truquillo para este método es enviar un correo a un destinatario falso pero que contenga el dominio correcto. Si el destinatario no existe, recibiremos un correo indicándonos que ha fallado la entrega, con lo cual tendremos un correo para investigar =P

### Registros DNS y DIG

Los registros DNS también nos pueden aportar información muy valiosa, para eso tenemos la herramienta de [SecurityTrails](https://securitytrails.com/), la cual nos permite comprobar los históricos de los registros DNS antes de añadirse a la red Cloudflare.

Tenemos 2 opciones:

#### _Búsqueda por registros de tipo A_

Buscamos el sitio web a auditar y nos dirigimos en el panel de la izquierda a “Historical Data”, de esta manera nos mostrará los registros de Tipo A y nos dirá directamente cual es la dirección IP real en caso de que esté almacenada.

![Registros tipo A con SecurityTrails](body/post3-image7.jpg)
_Registros tipo A con SecurityTrails_

#### _Búsqueda por registros NS_

Como anteriormente, pero una vez estemos en “Historical Data”, hacemos click en “NS”.

![Registros tipo NS con SecurityTrails](body/post3-image8.jpg)
_Registros tipo NS con SecurityTrails_

Con los registros NS a mano, utilizaremos la herramienta DIG para que nos devuelva la dirección IP real del servidor:

```bash
dig 
ns1.targetnameserver.com targetdomain.com
```

### Netcraft

Netcraft es una herramienta web muy útil, la cual nos brinda información del sitio web que queremos auditar. Podemos visualizar el histórico de los servidores donde se ha ido alojando el Sitio Web, así como los Nameserver, Site Rank, etc. Como he comentado, información muy útil. 

De esta manera, podemos comprobar también el histórico de las direcciones IP antes de ser añadido al servicio de Cloudflare.

Para ello accedemos a [Netcraft](https://toolbar.netcraft.com/site_report?url=) e introducimos el sitio web a auditar, directamente nos mostrará información relacionada con el sitio como se puede ver en la siguiente imagen.

![Información útil del sitio web a auditar](body/post3-image9.jpg)
_Información útil del sitio web a auditar_

## Probando y confirmando

Cuando hemos obtenido la dirección IP pública real del servidor donde está alojado el sitio web, tenemos que probar que verdaderamente funciona, para ello tenemos 2 opciones de saltarnos los servidores de la red de Cloudflare:

#### Opción 1

Añadir directamente el domino/subdominio y la dirección IP al archivo hosts:

![Añadir dirección IP y dominio al archivo Hosts](body/post3-image10.jpg)
_Añadir dirección IP y dominio al archivo Hosts_

#### Opción 2

Si vamos a utilizar Burpsuite para la auditoria o pentest, es recomendable asignar una resolución de nombre manual, de esta forma anularemos el reenvío hacia los servidores de Cloudflare y resolverá con la dirección IP añadida. Para ello:

![Resolución de nombre en Burpsuite](body/post3-image11.jpg)
_Resolución de nombre en Burpsuite_

## Conclusiones

Hay que tener en cuenta que ninguno de los métodos mostrados aquí es 100% fiable, es posible que a mi me sirva, pero a alguno de vosotros no. Lo mejor que se puede hacer es probar todos los métodos e investigar hasta conseguir la dirección IP correcta.

Cabe mencionar que la exposición de la direccion IP real del servidor, no se trata de ninguna vulnerabilidad de **Cloudflare**, más bien son fallos de configuración de los administradores del Sitio Web, exponiendo dominios o subdominios que no han sido añadidos correctamente al servicio de Cloudflare.

Como hemos podido observar, lo más importante en la primera fase de auditoría o Pentest, es la recolección de información, obtener direcciones IP de todo tipo para más tarde ir comprobando y descartando. 

Los servidores DNS siempre deben estar en el punto de mira ya que nos pueden mostrar información histórica y que siempre estará disponible en Internet.

Aquí abajo os dejo unas cuantas herramientas para la recopilación de información de Sitios Web, así como enumeración de subdominios, servicios, etc:

- [_DNSQueries_](https://www.dnsqueries.com/en/domain_check.php)
- [_DNSdumpster_](https://dnsdumpster.com/)
- [_Shodan_](https://www.shodan.io/search?query=)
- [_HatCloud_](https://github.com/HatBashBR/HatCloud)
- [_CloudPeler_](https://github.com/zidansec/CloudPeler) (_Nueva versión de Crimeflare_)
- [_CloudFail_](https://github.com/m0rtem/CloudFail)
- [_CloudIP_](https://github.com/Top-Hat-Sec/thsosrtl/blob/master/CloudIP/cloudip.sh)

Existen muchos otros métodos de detección, si alguno de vosotros quiere dejar un comentario con el que mejor le sirve en su día a día se lo agradecería =D

Nos vemos en el próximo artículo.

Saludos!

Referencias:

- <https://enciphers.com/bypassing-cloudflare-waf-to-get-more-vulnerabilities>
- <https://www.secjuice.com/finding-real-ips-of-origin-servers-behind-cloudflare-or-tor>
- <https://blog.detectify.com/2019/07/31/bypassing-cloudflare-waf-with-the-origin-server-ip-address>

