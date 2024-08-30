---
title: "Pivoting con Chisel - Túneles TCP/UDP sobre HTTP"
date: "2021-05-12"
categories: [Hacking]
tags: [Bypass-Firewall, Chisel, Hacking, Pentesting, Pivoting, Port-Forwarding, Red-Team]
media_subpath: /assets/img/posts/2021-05-12-herramienta-chisel-tuneles-tcp-udp-sobre-http
image:
   path: header/portada_chisel.webp
   lqip: data:image/webp;base64,UklGRooAAABXRUJQVlA4WAoAAAAQAAAAEwAACgAAQUxQSBQAAAABD3Dv/4iIICQgaP6/9iCi/ylxJFZQOCBQAAAAsAMAnQEqFAALAD85hrlTryklorAIAeAnCUAYG4Q5oGZi8OhNGgAA/slAobzGNcT4agjAkazgEgTjTAV7ZQAISX4N++nE62otfVHcW05mAAA=
   
published: true
---

Buenas lectores!

En esta entrada quiero hablaros de la herramienta **Chisel**. Esta herramienta la suelo utilizar bastante a la hora de realizar **Port-Forwarding** en ejercicios de pentesting, para **evadir firewalls** y realizar **pivoting** en redes internas.

## Descripción

El desarrollador **Jaime Pillora** define esta herramienta como :

> Chisel es un túnel TCP/UDP rápido, transportado a través de HTTP, protegido mediante SSH. Ejecutable único que incluye tanto al cliente como al servidor. Escrito en Go (golang). Chisel es principalmente útil para atravesar firewalls, aunque también se puede usar para proporcionar un punto final seguro en su red.

Os quiero mostrar a través de ejemplos como podemos realizar **port-forwarding** de puertos que son internos y no están públicos para el exterior o generar túneles con proxy **SOCKS** y **Proxychains** para poder reenviar tráfico a través de ellos y tener alcance a otras redes.

## Descargar y compilar

Podemos descargar Chisel a través del Github del autor:

- [https://github.com/jpillora/chisel](https://github.com/jpillora/chisel)

```bash
$ git clone https://github.com/jpillora/chisel
```

Una vez descargado, pasamos a compilar con flags y UPX para reducir el tamaño considerablemente:

```bash
$ go build -ldflags "-s -w"
(...)
$ upx brute chisel
(...)
$ du -hc chisel
3,2M	chisel
3,2M	total
```

Nos quedará el binario compilado, como bien indica el desarrollador, este mismo binario hace las funciones de cliente y servidor al mismo tiempo.

![](body/ba66ff9ae0082c399cd33c8333896a113c6395ef.png)

Si lo queremos utilizar para Windows, debemos bajar el ejecutable correspondiente, ya que este únicamente nos servirá para equipos GNU/Linux.

Binario **chisel** para **SO Windows**:

- [chisel\_1.7.6\_windows\_i386.gz](https://github.com/jpillora/chisel/releases/download/v1.7.6/chisel_1.7.6_windows_386.gz)

- [chisel\_1.7.6\_windows\_amd64.gz](https://github.com/jpillora/chisel/releases/download/v1.7.6/chisel_1.7.6_windows_amd64.gz)

## Escenarios

Voy a utilizar un pequeño laboratorio que he creado en un entorno virtual para mostrar los diferentes escenarios en los que podemos hacer uso de esta herramienta entre muchos otros. Las máquinas están en el mismo segmento de red, pero tienen reglas de firewall aplicadas.

![](body/43129f7c2738a4ae5085afe622ab40f887e41f84.png)

### Escenario 1

En este escenario, la **máquina A** enrutará el tráfico que vaya dirigido a su puerto local **9000** al puerto **80** de la **máquina Atacante**.

Atacante

```bash
$ ./chisel server -p 1337
```

Máquina A

```bash
$ ./chisel client 172.16.222.2:1337 9000:172.16.222.2:80
```

### Escenario 2

En este escenario, abriremos un puerto en nuestra **máquina atacante** (8080) que enturará el tráfico al puerto 8080 de la **máquina A** (_172.16.222.3_), de esta forma podemos traernos a nuestra máquina el puerto que queremos atacar de la **máquina A** y que no está expuesto externamente.

Atacante

```bash
./chisel server -p 1337 --reverse
```

Máquina A

```bash
./chisel client 172.16.222.3:1337 R:8080:127.0.0.1:8080
```

Atacante

```bash
$ curl -s http://localhost:8080 | html2text

****** Private Web ******
Only for members. Not Public
```

### Escenario 3

En este escenario, abriremos un puerto en nuestra **máquina Atacante** (9000) que enrutará el tráfico al puerto 80 de la **máquina B** (_172.16.222.4_). De esta forma podemos atacar un puerto de una máquina que no tenemos visibilidad pero sí que la tiene la **máquina A**.

Atacante

```bash
./chisel server -p 1337 --reverse
```

Máquina A

```bash
./chisel client 172.16.222.2:1337 R:9000:172.16.222.4:80
```

Atacante

```bash
$curl -s http://localhost:9000 | html2text

****** Debian Server Laboratory ******
Server IP: 172.16.222.4  Allow from: 172.16.222.3 - Ubuntu Server
```

### Escenario 4

En este escenario, crearemos un **túnel proxy SOCKS** que enrutará todo el tráfico de nuestra **máquina atacante** por el puerto 1080 (por defecto) de la herramienta proxychains a la **máquina B** (_172.16.222.4_), permitiéndonos utilizar la **máquina A** (_172.16.222.3_) como servidor de salto.

Atacante

```bash
./chisel server -p 1337 --reverse --socks
```

Máquina A

```bash
./chisel client 172.16.222.2:1337 R:socks

(por defecto puerto 1080 de proxychains, si queremos cambiar el puerto: R:PUERTO:socks)
```

Modificamos el archivo **/etc/proxychains.conf** :

![](body/5c89a00a23c3269113bbafa9c9b1347105a0537a-1.png)

Atacante

```bash
proxychains ./portScan.sh 172.16.222.4
```

![](body/cf8e98f804be4f264171ebe8ac1a0f73467d3bb6.png)

Tráfico

```bash
12:42:26.593966 IP 172.16.222.3.56758 > 172.16.222.4.21: Flags [S], seq 3743428595, win 64240, options [mss 1460,sackOK,TS val 661422675 ecr 0,nop,wscale 7], length 0
12:42:26.594117 IP 172.16.222.4.21 > 172.16.222.3.56758: Flags [S.], seq 898006718, ack 3743428596, win 65160, options [mss 1460,sackOK,TS val 3043963476 ecr 661422675,nop,wscale 7], length 0
12:42:26.595035 IP 172.16.222.3.56758 > 172.16.222.4.21: Flags [.], ack 1, win 502, options [nop,nop,TS val 661422675 ecr 3043963476], length 0
12:42:26.598495 IP 172.16.222.4.21 > 172.16.222.3.56758: Flags [P.], seq 1:21, ack 1, win 510, options [nop,nop,TS val 3043963480 ecr 661422675], length 20: FTP: 220 (vsFTPd 3.0.3)
12:42:26.598847 IP 172.16.222.3.56758 > 172.16.222.4.21: Flags [.], ack 21, win 502, options [nop,nop,TS val 661422680 ecr 3043963480], length 0
12:42:26.599081 IP 172.16.222.3.56758 > 172.16.222.4.21: Flags [P.], seq 1:2, ack 21, win 502, options [nop,nop,TS val 661422680 ecr 3043963480], length 1: FTP: 
12:42:26.599111 IP 172.16.222.4.21 > 172.16.222.3.56758: Flags [.], ack 2, win 510, options [nop,nop,TS val 3043963481 ecr 661422680], length 0
12:42:26.599325 IP 172.16.222.3.56758 > 172.16.222.4.21: Flags [F.], seq 2, ack 21, win 502, options [nop,nop,TS val 661422680 ecr 3043963480], length 0
12:42:26.599432 IP 172.16.222.4.21 > 172.16.222.3.56758: Flags [F.], seq 21, ack 3, win 510, options [nop,nop,TS val 3043963481 ecr 661422680], length 0
12:42:26.606306 IP 172.16.222.3.56758 > 172.16.222.4.21: Flags [.], ack 22, win 502, options [nop,nop,TS val 661422682 ecr 3043963481], length 0
```

Podemos ver cómo el tráfico generado es originado desde la **máquina de salto A** (_172.16.222.3_).

## Conclusión

Como habéis podido ver, esta es una buena herramienta para realizar port-forwarding cuando no tenemos acceso por SSH para utilizar este. Es posible utilizar el servidor en GNU/Linux y el cliente en Windows o viceversa.

**Chisel** tiene parámetros interesantes, como: **_fingerprint_**, **_auth_**, **_authkey_**, **_etc_** para hacer de nuestra conexión más segura a la hora de realizar túneles.

En próximas entradas enseñaré cómo realizar doble pivoting cuando estamos atacando una red segmentada y obtener shell inversa reenviando puertos y tráfico.

Gracias por leerme.

Saludos!
