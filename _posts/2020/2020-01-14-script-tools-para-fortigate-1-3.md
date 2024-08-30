---
title: "Script Tools para Fortigate 1/3"
date: "2020-01-14"
categories: [Fortigate, Tools]
tags: [Fortigate, Scripts, Tools, Firewall]
media_subpath: /assets/img/posts/2020-01-14-script-tools-para-fortigate-1-3/
image:
  path: header/portada_scriptools.webp
  lqip: data:image/webp;base64,UklGRlgAAABXRUJQVlA4IEwAAABQAwCdASoUAAsAPzmEuVOvKKWisAgB4CcJZTuAABL09H/MgAD+7fMS9MS8nR1cYNRGV4hSvrZlk71SG4rYg/Dw2Um3XFSXUKwt+gAA

published: true
---

¡Hola compañeros!

Quiero realizar un total de 3 entradas rápidas mostrando los scripts tools que realicé en su día cuando administraba firewalls **Fortigate**.

En nuestro día a día trabajando en ciberseguridad necesitamos respuestas rápidas para comportamientos extraños o sospechosos, para el caso de bloquear o banear direcciones IP en los perimetrales se prioriza el **automatizar** las acciones que conllevan tener que dar demasiados clics o movernos por la GUI de la plataforma que estemos administrando.

Estos scripts utilizan la  shell interactiva **EXPECT** en sistemas GNU/Linux, la cual nos permite enviar comandos y esperar respuesta para nuevamente enviar comandos.

Instalación de "Expect":

```bash
sudo apt update && sudo apt install expect -y
```

> Para el que quiera saber un poquito más de **_Expect_**, dejo aquí el [man page](https://linux.die.net/man/1/expect)

Para la creación de estos scripts, me basé en la entrada del **Blog Inseguros** de **KinoMakino**, la cual dejaré al final de esta entrada por si queréis echarle un ojo y poneros en contexto, aunque dudo que todavía no lo conozcáis =P

La intención que tenía en su día, era la de crear un panel de administración web en la cual mediante PHP y MySQL, realizar la llamada de estos scripts en función de los clientes, así como para tener un apartado threat intelligent donde quedasen recogidos todos los **IOC's**, en este caso con direcciones IP que fuesen añadiéndose en cada interacción.

Yo lo definía como un panel de herramientas adicional que sirviese de apoyo para los analistas: _banear direcciones, consultar, escanear con API de Virustotal, de Spamhaus_...vamos, ideas locas que se quedaron en el baúl.

Como veréis, son sencillos pero aún así explicaré las funciones de cada uno de ellos en sus respectivas entradas.

> Dejo mi **Github** con los Scripts por aquí para el que los quiera utilizar:
> 
> [https://github.com/rekkatz/scripts\_tools\_fortigate](https://github.com/rekkatz/scripts_tools_fortigate)

## Banear direcciones IP

El primero de los scripts tiene como objetivo realizar un _**baneo rápido de una dirección IP**_ la cual ha sido detectada intentando realizar conexiones o acciones sospechosas:

```bash
#!/usr/bin/expect -f

# Variables
set IP [lindex $argv 0];
set COM [lindex $argv 1];
set timeout 2;

# Logs
log_user 0
log_file -a <path_save_log>

# Execution command to client Fortigate CLI
puts "############################################"
puts "#### Añadiendo IP a grupo de Blacklist #####"
puts "############################################"
spawn ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=~/.ssh/known_hosts" <USER@IP> -p 22
expect "password: "
send "<YOUR_PASSWORD>\r"
expect "#"
send "config firewall address\r"
expect "(address)"
send "edit BL_$IP\r"
expect "BL_$IP"
send "set subnet $IP/32\r"
expect {
    "invalid" {
        puts "\n++ ERROR - La dirección IP $IP no es correcta"
        puts "** Por favor, comprueba que ha sido introducida correctamente\n"
        exit
        }
}
send "set comment \"$COM\"\r"
expect "(BL_$IP)"
send "set color 6\r"
expect "(BL_$IP)"
send "end\r"
expect "#"
send "config firewall addrgrp\r"
expect "(addrgrp)"
send "edit BLACKLIST\r"
expect "(BLACKLIST)"
send "append member BL_$IP\r"
expect "(BLACKLIST)"
send "end\r"
expect "#"
send "exit\r"
expect "closed"
puts "\nOK - Dirección $IP añadida a grupo Blacklist\n"
```

Sintaxis del comando:

```bash
./ban.sh "IP TO BAN" "Comment"

Ejemplo:
./ban.sh 2.2.2.2 "IPS Detect"
```

>_El argumento "Comentario" es opcional. Pero es una buena práctica introducir la relación del bloqueo de la dirección IP para tenerla identificada._

Este script crea un grupo de direcciones como objeto llamado **BLACKLIST** en el cual introduce un objeto de dirección IP que queremos bloquear con un prefijo de _**BL\_**_ y con color de objeto 6 (Rojo), también introducimos un comentario para llevar un control del por qué ha sido baneada. Cada vez que este script es ejecutado, se registra las acciones realizadas en un archivo log.

![Resultado de ejecución de script para baneo](body/post5-image1.jpg)
_Resultado de ejecución de script para baneo_

## Desbanear direcciones IP

Exactamente igual que el anterior script, pero permitiéndonos _**eliminar una dirección IP del grupo de BLACKLIST**_ en el cual ha sido añadido.

Este script viene bien cuando se ha introducido una dirección IP errónea y queremos eliminarla del grupo:

```bash
#!/usr/bin/expect -f

# Variables arguments
set IP [lindex $argv 0];
set timeout 2;

# Log file threat intelligent
log_user 0
log_file <path_save_log>

# Execution command to client Fortigate CLI
puts "############################################"
puts "#### Eliminando IP del grupo Blacklist #####"
puts "############################################"
spawn ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=~/.ssh/known_hosts" <USER@IP> -p 22
expect "password: "
send "<YOUR_PASSWORD>\r"
expect "\#"
send "config firewall addrgrp\r"
expect "(addrgrp)"
send "edit BLACKLIST\r"
expect "(BLACKLIST)"
send "unselect member BL_$IP\r"
expect {
    "entry not found" {
        puts "\n++ ERROR - La dirección IP $IP no se encuentra en el grupo BLACKLIST\n"
        exit
        }
}
send "end\r"
expect "#"
send "config firewall address\r"
expect "(address)"
send "delete BL_$IP\r"
expect "(address)"
send "end\r"
expect "#"
send "exit\r"
expect "closed"
puts "\n++ OK - Dirección IP $IP eliminada del grupo BLACKLIST\n"
```

Sintaxis del comando:

```bash
./unban.sh "IP TO UNBAN"

Ejemplo:
./unban.sh 2.2.2.2
```

No hay mucho que comentar, se conecta por **SSH al firewall** y a través de **CLI** eliminamos la dirección IP deseada pasándola como argumento. Se mantiene el grupo de BLACKLIST pero se elimina el objeto dirección IP.

![Resultado de ejecución de script para desbaneo](body/post5-image2.jpg)
_Resultado de ejecución de script para desbaneo_

Estos son los scripts principales para banear y desbanear direcciones IP. Se puede mejorar de mil maneras, añadiendo nuevas variables o condicionales, cada uno en su día a día irá viendo que le hace falta o que no, modificándolo a su antojo.

Uno de los problemas que tiene, es que la password se  puede ver en texto plano directamente dentro del archivo, pero podemos utilizar private key sin problema, añadiendo la opción para SSH de utilizar private key (-i) con su respectiva localización de esta.

Para que esto funcione, lógicamente tienen que existir _**políticas IPv4 configuradas**_ en el firewall que tengan con acción "**Deny**" el origen, destino o ambos con el objeto grupo de direcciones BLACKLIST como referencia.

Como podréis ver no soy ningún experto en programación xD simplemente he intentado añadir algo nuevo al script de KinoMakino que me servía en mi día a día. Es lo bonito de compartir, coges algo y lo modificas a tu gusto y lo vuelves a compartir para que otro intente añadir algo más.

Muchas gracias por leerme.

Espero que les sirva de ayuda, cualquier duda podéis dejarla en los comentarios.

Saludos!

Referencias:

- <https://kinomakino.blogspot.com/2017/03/scripts-en-bash-para-banear-ip-desde.html>
