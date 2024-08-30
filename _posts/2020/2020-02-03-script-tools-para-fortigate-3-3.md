---
title: "Script Tools para Fortigate 3/3"
date: "2020-02-03"
categories: [Fortigate, Tools]
tags: [Fortigate, Scripts, Tools, Firewall]
media_subpath: /assets/img/posts/2020-02-03-script-tools-para-fortigate-3-3
image:
   path: header/portada_scriptools.webp
   lqip: data:image/webp;base64,UklGRlYAAABXRUJQVlA4IEoAAACQAwCdASoUAAsAPzmEuVOvKKWisAgB4CcJZQAAXGMglKHA6ogAAP7nYPwoH68fxNpSGsOKdC0N/OlPpsP67KbS7+66ha//yAAAAA==
   
published: true
---


¡Hola compañeros!

En esta tercera y última entrada, quiero mostrar el último script realizado para fiewalls **Fortigate**. Esta ve el objetivo del script será la de ralizar backups del firewall a través de línea de comandos, como podréis ver no es nada del otro mundo, solo basta jugar un poco con "**Expect**".

**Importante**: Para poder realizar bakcups a través de línea de comandos, necesitaremos habilitar en fortigate la opción de SCP para la transferencia del archivo CONF.

```shell
Fortigate # config system global
Fortigate # set admin-scp enable
Fortigate # end
```

## Código del Script

```bash
#!/usr/bin/expect -f

# Variables definidas
set PATH [lindex $argv 0];
set DATE [exec date +%d%m%Y_%H%M];
set CONFIG "sys_config"
set timeout 2;

# Log file
log_file <PATH_SAVE_LOG>
log_user 0

# Execution command to client Fortigate CLI
spawn scp -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=~/.ssh/known_hosts" -P 22 <USER@IP>:$CONFIG $PATH/
backup\_$DATE.conf
expect "password: "
send "password\r"
puts "#####################################"
puts "# Realizando Backup a través de SCP #"
puts "#####################################"
log_user 1
expect eof
puts "\r"
```

#### Sintaxis del comando a ejecutar:

```bash
./4-backup_conf.sh <Path to save>
```

#### Output del comando:

![Output del comando](body/post7-image1.jpg)
_Output del comando_


![Lista de backups en ruta](body/post7-image2.jpg)
_Lista de backups en ruta_

Pues bueno, este ha sido el último "script", por llamarlo de alguno forma, ya que simplemente le he añadido algunas variables y código adicional, pero la esencia está en el SCP.

Se pueden añadir variables nuevas y demás si tenéis una ruta por defecto para guardar los backups, de esta forma no haría falta añadirla como argumento en la ejecución del comando.

Si queréis automatizar la ejecución y llevar un control de los backups, podéis añadirlo a CRON especificando el tiempo.

Bueno, espero que os haya servido de ayuda, si quereís añadir alguna opinión, crítica, etc, podéis dejarlo abajo en los comentarios.

Nos vemos en el próximo artículo.

Saludos!
