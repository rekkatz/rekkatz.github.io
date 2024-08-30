---
title: "Bandit 0 - 10 | OverTheWire"
date: "2021-05-20"
categories: [Write-Ups, OverTheWire]
tags: [Bandit, Bash, Ctf, Hacking, OverTheWire, Scripting, Write-Up]
media_subpath: /assets/img/posts/2021-05-20-bandit-0-al-10-overthewire
image:
   path: header/portada_overthewire.webp
   lqip: data:image/webp;base64,UklGRkgAAABXRUJQVlA4IDwAAADwAgCdASoUAAsAPzmEulOvKKWisAgB4CcJaQAAetCiQAD+6G1czDb8GC3BbKDffAa61dng5TCPWs98AAA=
   
published: true
---

En esta entrada y en las próximas, mostraré los tipos de resoluciones que se necesitan a la hora de superar los retos de la serie **Bandit** de la plataforma **OverTheWire**.

Antes de nada quiero comentar que si estás realizando Bandit en OTW, intentes realizarlo por tu propia cuenta, leyendo las páginas man de los comandos y experimentando con lo que venga a la cabeza para intentar superar el reto o nivel, esto te ayudará a investigar y utilizar comandos de la shell y poder desenvolverte con mayor soltura en la terminal.

Una vez resuelvas el reto, no te quedes con lo último que has realizado, busca diferentes alternativas para aprender de nuevos métodos y comandos.

## Descripción

Como descripción de esta serie **Bandit**, voy a reflejar la propia descripción de la plataforma:

> "_Bandit está dirigido a principiantes absolutos. Le enseñará los conceptos básicos necesarios para poder jugar a otros juegos o series de mayor dificultad_"

## Nota para principiantes

Este juego está organizado en niveles. Empiezas en el nivel 0 y tratas de superarlo. Terminar un nivel da como resultado la información sobre cómo comenzar el siguiente nivel (Level Goal). Para superar el reto, necesitaremos obtener la bandera para el siguiente nivel que será la contraseña para acceder al siguiente reto por SSH, el usuario irá aumentando según el nivel de reto: _bandit1_, _bandit2_, _bandit3_, _etc_.

Te encontrarás con muchas situaciones en las que no tienes idea de lo que se supone que debes hacer. ¡Que no cunda el pánico! ¡No te rindas!

El proposito de este juego es que aprendas los conceptos básicos. Parte de aprender lo básico es leer mucha información nueva.

Hay varias cosas que puedes intentar hacer cuando no esté seguro de cómo continuar:

1. Si conoce un comando, pero no sabe como usarlo, pruebe el manual (man <comando>). El comando "man" tambien tiene un manual, pruébalo. Presione `q` para salir del comando man.
2. Si no hay página de mnaual, el comando puede tener la ayuda integrada en el mismo. Pruebe a utilizar `<comando> help` para visualizar el panel de ayuda de dicho comando.
3. Tu mejor amigo es google cuando te quedes estancado. ¡Aprende a utilizarlo correctamente!

## Retos Bandit 0 → 10

### Nivel 0

Objetivo:

_El objetivo de este nivel es que inicies sesión en el juego mediante SSH. El host al que debe conectarse es `bandit.labs.ojectedwire.org` , en el puerto 2220. El nombre de usuario es bandit0 y la contraseña es bandit0 . Una vez que haya iniciado sesión, vaya a la página de Nivel 1 para averiguar cómo superar el Nivel 1._

```bash
ssh bandit0@bandit.labs.overthewire.org -p 2220
PASSWORD: bandit0

bandit0@bandit:~$
```

### Nivel 0 → 1

Objetivo:

_La contraseña para el siguiente nivel se almacena en un archivo llamado "readme" ubicado en el directorio de inicio. Utilice esta contraseña para iniciar sesión en bandit1 mediante SSH. Siempre que encuentre una contraseña para un nivel, use **SSH** (en el puerto **2220**) para iniciar sesión en ese nivel y continuar el juego._

Resolución:

```bash
bandit0@bandit:~$ ls -l
total 4
-rw-r----- 1 bandit1 bandit0 33 May  7  2020 readme

bandit0@bandit:~$ cat readme
boJ9jbbUNNfktd78OOpsqOltutMc3MY1
```

Alternativas para lectura de bandera:

```bash
bandit0@bandit:~$ ls | xargs cat
boJ9jbbUNNfktd78OOpsqOltutMc3MY1

bandit0@bandit:~$ ls -l | tail -n1 | awk 'NF{print$NF}' | xargs cat
boJ9jbbUNNfktd78OOpsqOltutMc3MY1

bandit0@bandit:~$ ls -l | tail -n1 | cut -d ' ' -f 11 | xargs cat
boJ9jbbUNNfktd78OOpsqOltutMc3MY1
```

### Nivel 1 → 2

Objetivo:

_La contraseña para el siguiente nivel se almacena en un archivo llamado "**\-**" ubicado en el directorio de inicio._

Resolución:

```bash
bandit1@bandit:~$ ls -l
total 4
-rw-r----- 1 bandit2 bandit1 33 May  7  2020 -

bandit1@bandit:~$ cat < -
CV1DtqXWVFXTvM2F0k09SHz0YwRINYA9
```

Alternativas para leer la bandera:

```bash
# Alternativa 1
bandit1@bandit:~$ cat < *
CV1DtqXWVFXTvM2F0k09SHz0YwRINYA9

# Alternativa 2
bandit1@bandit:~$ cat ./*
CV1DtqXWVFXTvM2F0k09SHz0YwRINYA9

# Alternativa 3
bandit1@bandit:~$ cat ./-
CV1DtqXWVFXTvM2F0k09SHz0YwRINYA9
```

### Nivel 2 → 3

Objetivo:

_La contraseña para el siguiente nivel se almacena en un archivo llamado "**spaces in this filename**" ubicado en el directorio de inicio._

Resolución:

```bash
bandit2@bandit:~$ ls -l
total 4
-rw-r----- 1 bandit3 bandit2 33 May  7  2020 spaces in this filename

bandit2@bandit:~$ cat "spaces in this filename"
UmHadQclWmgdLOKQ3YNgjWxGoRMb5luK
```

Alternativas para leer la bandera:

```bash
# Alternativa 1
bandit2@bandit:~$ cat spaces\\ in\\ this\\ filename
UmHadQclWmgdLOKQ3YNgjWxGoRMb5luK

# Alternativa 2
bandit2@bandit:~$ cat *
UmHadQclWmgdLOKQ3YNgjWxGoRMb5luK
```

### Nivel 3 → 4

Objetivo:

_La contraseña para el siguiente nivel se almacena en un archivo oculto en el directorio "**inhere**"._

Resolución:

```bash
ssh bandit3@bandit.labs.overthewire.org -p 2220
PASSWORD: UmHadQclWmgdLOKQ3YNgjWxGoRMb5luK

bandit3@bandit:~$ ls -l
total 4
drwxr-xr-x 2 root root 4096 May  7  2020 inhere

bandit3@bandit:~$ cd inhere/
bandit3@bandit:~/inhere$ ls -la
total 12
drwxr-xr-x 2 root    root    4096 May  7  2020 .
drwxr-xr-x 3 root    root    4096 May  7  2020 ..
-rw-r----- 1 bandit4 bandit3   33 May  7  2020 .hidden

bandit3@bandit:~/inhere$ cat .hidden
pIwrPrtPN36QITSp3EQaw936yaFoFgAB
```

### Nivel 4 → 5

Objetivo:

_La contraseña para el siguiente nivel se alamcena en un archivo con la propiedad "**only human-readable**" en el directorio "**inhere**"._

Resolución de nivel 4 de la serie Bandit en plataforma OverTheWire

```bash
bandit4@bandit:~$ ls -l
total 4
drwxr-xr-x 2 root root 4096 May  7  2020 inhere

bandit4@bandit:~$ cd inhere/
bandit4@bandit:~/inhere$ ls -l
total 40
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file00
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file01
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file02
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file03
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file04
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file05
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file06
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file07
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file08
-rw-r----- 1 bandit5 bandit4 33 May  7  2020 -file09

bandit4@bandit:~/inhere$ file ./*
./-file00: data
./-file01: data
./-file02: data
./-file03: data
./-file04: data
./-file05: data
./-file06: data
./-file07: ASCII text
./-file08: data
./-file09: data

bandit4@bandit:~/inhere$ cat ./-file07
koReBOKuIDDepwhWk7jZC0RTdopnAYKh
```

Alternativas para leer la bandera:

```bash
# Alternativa 1
bandit4@bandit:~$ find inhere/ -type f -readable | xargs file
inhere/-file01: data
inhere/-file00: data
inhere/-file06: data
inhere/-file03: data
inhere/-file05: data
inhere/-file08: data
inhere/-file04: data
inhere/-file07: ASCII text
inhere/-file02: data
inhere/-file09: data
bandit4@bandit:~$ find inhere/ -type f -readable | grep 07 | xargs cat
koReBOKuIDDepwhWk7jZC0RTdopnAYK

# Alternativa 2
bandit4@bandit:~/inhere$ cat ./*; echo
�/`2ғ�%��rL~5�g��� �������p,k�;��r*��	�.!��C��J	�dx,�e�)�#��5��
                                                                       ��p��V�_���ׯ�mm�����h!TQO�`�4?��r�l$�?h�9('���!y�e�#�x�O��=�ly���~��A�f����-E�{���m�����ܗMkoReBOKuIDDepwhWk7jZC0RTdopnAYKh
�T�?�i��j��îP�F�l�n��J����{��@�e�0$�in=��_b�5FA�P7sz��gNT

# Alternativa 3
bandit4@bandit:~/inhere$ strings ./*
!TQO
koReBOKuIDDepwhWk7jZC0RTdopnAYKh
```

### Nivel 5 → 6

Objetivo:

_La contraseña para el siguiente nivel se almacena en un archivo en algún lugar del directorio "**inherit**" y tiene todas las siguientes propiedades:_

- legible por humanos
- 1033 bytes
- no ejecutable

```bash
bandit5@bandit:~$ find ./inhere/ -readable -size 1033c ! -executable
./inhere/maybehere07/.file2

bandit5@bandit:~$ find ./inhere/ -readable -size 1033c ! -executable | xargs cat
DXjZPULLxYr17uwoI01bNLQbtFemEgo7

# El anterior archivo que contiene la bandera, tiene espacios en blanco al final de este, podemos eliminarlos con sed:

bandit5@bandit:~$ find ./inhere/ -readable -size 1033c ! -executable | xargs cat | sed '/^\\s/d'
DXjZPULLxYr17uwoI01bNLQbtFemEgo7
```

### Nivel 6 → 7

Objetivo:

_La contraseña para el siguiente nivel se almacena en algún lugar del servidor y tiene todas las siguientes propiedades:_

- Usuario propietario bandit7
- Grupo propietario bandit6
- Tamaño 33bytes

```bash
bandit6@bandit:~$ find / -user bandit7 -group bandit6 -size 33c 2>/dev/null | xargs ls -l
-rw-r----- 1 bandit7 bandit6 33 May  7  2020 /var/lib/dpkg/info/bandit7.password

bandit6@bandit:~$ find / -user bandit7 -group bandit6 -size 33c 2>/dev/null | xargs cat
HKBPTKQnIay4Fw76bEy8PVxKEDQRKTzs
```

Alternativas para leer bandera:

```bash
bandit6@bandit:~$ find / -user bandit7 -group bandit6 -size 33c -exec ls -l {} \\; 2>/dev/null
-rw-r----- 1 bandit7 bandit6 33 May  7  2020 /var/lib/dpkg/info/bandit7.password

bandit6@bandit:~$ find / -user bandit7 -group bandit6 -size 33c -exec cat {} \\; 2>/dev/null
HKBPTKQnIay4Fw76bEy8PVxKEDQRKTzs
```

### Nivel 7 → 8

Objetivo:

_La contraseña para el siguiente nivel se almacena en el archivo **"data.txt**" junto a la palabra "**millionth**"._

```bash
bandit7@bandit:~$ ls -l
total 4088
-rw-r----- 1 bandit8 bandit7 4184396 May  7  2020 data.txt

bandit7@bandit:~$ grep -i "millionth" data.txt
millionth	cvX2JJa4CFALtqS87jk27qwqGhBM9plV

# Alternativa para quedarnos solo con la bandera:
bandit7@bandit:~$ grep -i "millionth" data.txt | awk 'NF{print$NF}'
cvX2JJa4CFALtqS87jk27qwqGhBM9plV
```

### Nivel 8 → 9

Objetivo:

_La contraseña para el siguiente nivel se almacena en el archivo "**data.txt**" y es la única línea de texto que aparece solo una vez._

```bash
bandit8@bandit:~$ ls -l
total 36
-rw-r----- 1 bandit9 bandit8 33033 May  7  2020 data.txt

bandit8@bandit:~$ sort data.txt | uniq -u
UsvVyFSfZZWbi6wgC7dAFyFuR6jQQUhR
```

### Nivel 9 → 10

Objetivo:

_La contraseña para el siguiente nivel se almacena en el archivo "**data.txt**" en una de las pocas cadenas legibles por humanos, precedida por varios caracteres "**\=**"._

```bash
bandit9@bandit:~$ ls -l
total 20
-rw-r----- 1 bandit10 bandit9 19379 May  7  2020 data.txt

bandit9@bandit:~$ strings data.txt | grep -n '='
13:========== the*2i"4
16:=:G e
61:========== password
77:<I=zsGi
83:Z)========== is
116:A=|t&E
154:Zdb=
163:c^ LAh=3G
188:*SF=s
192:&========== truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk
207:S=A.H&^
```

Alternativas para afinar y quedarnos únicamente con la bandera, existen otras muchas alternativas, estas son algunas:

```bash
# Alternativa 1
bandit9@bandit:~$ strings data.txt | sed -n '192p' | awk 'NF{print$NF}'
truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk

# Alternativa 2
bandit9@bandit:~$ strings data.txt | grep '=' | tail -n 2 | head -n 1 | cut -d ' ' -f 2
truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk

# Alternativa 3
bandit9@bandit:~$ strings data.txt | grep -oP '=.{10,}'
========== the*2i"4
========== password
========== is
========== truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk

bandit9@bandit:~$ strings data.txt | grep -oP '=.{10,}' | awk 'FNR>=4 && NF{print$NF}'
truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk

# Alternativa 4
bandit9@bandit:~$ strings data.txt | egrep -n '=' | egrep '192' | awk 'NF{print$NF}'
truKLdjsbJ5g7yyJ2X2R0o3a5HQJFuLk
```
