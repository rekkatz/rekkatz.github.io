---
title: "Script Tools para Fortigate 2/3"
date: "2020-01-17"
categories: [Fortigate, Tools]
tags: [Fortigate, Scripts, Tools, Firewall]
media_subpath: /assets/img/posts/2020-01-17-script-tools-para-fortigate-2-3
image:
   path: header/portada_scriptools.webp
   lqip: data:image/webp;base64,UklGRloAAABXRUJQVlA4IE4AAADwAwCdASoUAAsAPzmGuVOvKSWisAgB4CcJZQAAXE8Kqpjt2yZ0XSgAAP7nISxaHe7z/w6yQgnXVfGxIcb0bDsfxqc7P/JH4PaUC5AAAAA=
   
published: true
---

¡Hola compañeros!

Segunda entrada dedicada a herramientas creadas para firewalls **Fortigate**.

Esta entrada y la que viene serán cortas, ya que los scripts creados para tal son muy sencillos.

En este caso mostráre un script creado en **Expect** para realizar consultas por CLI al firewall, con destino de búsqueda el grupo de _**BLACKLIST**_ creado en el [post anterior](https://www.bypasseados.com/2020/01/scripts-tools-fortigate-1.html).

De esta forma podremos consultar si una determinada dirección IP se encuentra como referencia dentro de este grupo o no.

## Consultar direcciones IP

Con la ejecución de este script, no introducimos ningún comando de configuración, simplemente realizamos consultas.

Como el output de este comando en crudo suele ser un tanto "simplón", he tenido que añadir la opción _**"-c"**_ en el comando **grep** _(grep -c)_, que de esta forma nos mostrará en cuantas líneas ha realizado match la dirección IP, por la tanto siempre deberá ser únicamente en 1, ya que no puede existir la dirección IP duplicada. En el caso de que no exista la dirección IP, obviamente no será matcheada en ninguna, por lo tanto el output será 0:

Así se muestra el output del comando normalmente:

![Dirección IP encontrada en el grupo Blacklist](body/post6-image1.jpg)
_Dirección IP encontrada en el grupo Blacklist_

![Dirección IP NO encontrada en el grupo Blacklist](body/post6-image2.jpg)
_Dirección IP NO encontrada en el grupo Blacklist_

Y así se muestra con la opción "**\-c**" de del comando "**grep**":

![Dirección IP encontrada en el grupo Blacklist \= 1](body/post6-image3.jpg)
_Dirección IP encontrada en el grupo Blacklist = 1_

![Dirección IP NO encontrada en el grupo Blacklist = 0](body/post6-image4.jpg)
_Dirección IP NO encontrada en el grupo Blacklist = 0_

Código del script:

```bash
#!/usr/bin/expect -f

# Variables
set IP [lindex $argv 0];
set timeout 2;

# Log file
log_user 0
log_file <PATH_SAVE_LOG>

# Execution command to client Fortigate CLI
spawn ssh -o "StrictHostKeyChecking=no" -o "UserKnownHostsFile=~/.ssh/known_hosts" <USER@IP> -p 22
expect "password: "
send "password\r"
expect "#"
send "show firewall addrgrp BLACKLIST | grep -c BL_$IP\r"
expect {
    "0" { puts "\n-- NOT FOUND - La dirección IP $IP NO se encuentra en el grupo BLACKLIST\n" }
    "1" { puts "\n++ FOUND - La dirección IP $IP se encuentra en el grupo BLACKLIST\n" }
}
send "exit\r"
expect "closed" 
```

Como podéis ver, es bastante básico y nos basamos en el output 0 y 1 para determinar si la dirección IP se encuentra en el grupo indicado:

![Output Script dirección IP encontrada](body/post6-image5.jpg)
_Output Script dirección IP encontrada_

![Output Script dirección IP NO encontrada](body/post6-image6.jpg)
_Output Script dirección IP NO encontrada_

Dejo como siempre mi **Github** por si alguien quiere utilizar/modificar estas herramientas a su gusto.

> Github - Script Tools Fortigate
> 
> [https://github.com/rekkatz/scripts\_tools\_fortigate](https://github.com/rekkatz/scripts_tools_fortigate)

Si alguno quiere dejar sus comentarios, ideas, opiniones, etc es libre de hacerlo y siempre son bienvenidos.

Gracias por leerme.

Saludos!
