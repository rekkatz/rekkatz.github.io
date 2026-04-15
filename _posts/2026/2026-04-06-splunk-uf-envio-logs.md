---
title: "Splunk UF en Linux: envío de logs desde endpoints"
date: "2026-04-06"
categories: [SIEM, Splunk]
tags: [splunk, universal-forwarder, ingestion, data-pipeline, linux]
media_subpath: /assets/img/posts/2026-04-06-splunk-uf-envio-logs
image:
   path: header/card_splunk_uf_linux.webp
   lqip: data:image/webp;base64,UklGRlwAAABXRUJQVlA4IFAAAABwAwCdASoUABQAPzmOvlevKacpqAqp4CcJZgCxHy/Ao00UQIAA+ZgNaf1szFpWmsmpvf8Odj/BGh2UX1V1BpGJbHdQuWJWadGC1j7DncnAAA==
published: true
---

## Introducción

En este artículo vamos a dar el siguiente paso dentro de un entorno SIEM: empezar a **ingerir datos reales**.

Para ello, utilizaremos el **Universal Forwarder (UF)** de Splunk, que nos permitirá enviar logs desde una máquina Linux hacia nuestra instancia de Splunk.

![Flujo de datos UF hacia Indexer](body/splunk-uf-data-flow.webp)

Este punto es importante, porque a partir de aquí dejamos de trabajar con datos simulados y empezamos a construir un entorno más cercano a lo que te vas a encontrar en escenarios reales.

## ¿Qué es el Universal Forwarder?

El **Universal Forwarder (UF)** es un agente ligero desarrollado por Splunk que se instala en endpoints o servidores para recolectar información local y enviarla a Splunk.

En entornos reales también existe otro tipo de forwarder, conocido como **Heavy Forwarder (HF)**, que incorpora capacidades adicionales como parsing, filtrado o routing de eventos, pero en la mayoría de despliegues, el Universal Forwarder es la opción más utilizada para la recolección de logs en endpoints debido a su bajo consumo de recursos.

**Características principales:**

- Bajo consumo de recursos
- Envío eficiente y continuo de eventos
- Comunicación segura (por defecto puerto 9997)
- Uso extendido en entornos productivos

En arquitecturas sencillas, los forwarders envían los datos directamente a los indexers, que son los encargados de procesarlos y almacenarlos. Sin embargo, en entornos reales es bastante habitual introducir **capas intermedias**, conocidas como colectoras, entre los sistemas origen y los indexers finales.

Estas colectoras suelen implementar **Heavy Forwarders (HF)**, que permiten realizar tareas adicionales como filtrado, normalización, enrutado o preprocesado de eventos antes de su indexación.

Este tipo de arquitectura aporta mayor control sobre los datos y facilita la escalabilidad en entornos con múltiples fuentes de información.

## Descarga e instalación del UF

El proceso de instalación es bastante directo: descarga del paquete, descompresión en `/opt` y ajuste de permisos.

>👉 https://www.splunk.com/en_us/download/universal-forwarder.html


**Instalación en Linux**

Descargamos el paquete del Universal Forwarder desde la web oficial de Splunk y lo descomprimimos en /opt:

```bash 
wget -O splunkforwarder.tgz "<URL_REAL_DEL_PAQUETE>"
sudo tar -xvzf splunkforwarder.tgz -C /opt
sudo useradd -m -s /bin/bash splunk
sudo chown -R splunk:splunk /opt/splunkforwarder
```

### Primer arranque

En el primer arranque es necesario aceptar la licencia. Además, es posible que Splunk solicite crear las credenciales de administrador:

```bash
sudo /opt/splunkforwarder/bin/splunk start --accept-license
```

Una vez iniciado, puedes comprobar la versión instalada:

```bash
sudo -u splunk /opt/splunkforwarder/bin/splunk version
```

![Versión del Universal Forwarder](body/splunk-uf-version.webp)

### Habilitar arranque automático

Para evitar tener que iniciar el forwarder manualmente tras cada reinicio, habilitamos el arranque automático:

```bash 
sudo /opt/splunkforwarder/bin/splunk enable boot-start -user splunk
```

Dependiendo de la distribución, Splunk se integrará con systemd o con init, aunque en sistemas actuales lo habitual es systemd.

Una vez configurado, gestionamos el servicio así:

```bash
sudo systemctl start SplunkForwarder
sudo systemctl status SplunkForwarder
```

![Estado del servicio SplunkForwarder](body/splunk-uf-systemctl-status.webp)

Durante el arranque es posible ver warnings relacionados con los permisos de SPLUNK_HOME:

>Attempting to revert the SPLUNK_HOME ownership

Estos warnings no afectan a la funcionalidad y pueden ser ignorados.

## Habilitar recepción en Splunk (Indexer)

Para que Splunk pueda recibir datos desde los forwarders, es necesario habilitar el puerto de recepción (9997 TCP) en el Indexer:

```bash
sudo -u splunk /opt/splunkforwarder/splunk/bin/splunk enable listen 9997
```

![Puerto 9997 habilitado en Splunk](body/splunk-receiving-port.webp)

Este comando habilita la recepción de datos en el puerto 9997 para forwarders.

Puedes comprobar que está escuchando correctamente:

```bash
ss -lntp | grep 9997
```

## Configuración de envío de logs

En este punto, es donde realmente defines qué datos quieres enviar y a dónde en el UF.

![Diagrama Inputs vs Outputs](body/splunk-uf-inputs-outputs.webp)

Implementaremos estas configuraciones directamente en el directorio `/opt/splunkforwarder/etc/system/local/` 

Elegimos esta ruta por ser la más directa en un entorno de pruebas, ya que posee la prioridad más alta en la jerarquía de directorios de Splunk (*lo veremos en próximos artículos*).

En esta ubicación definiremos tanto el archivo **inputs.conf** (fuentes de datos) como el **outputs.conf** (destino de los datos). 

Cabe destacar, que en entornos de producción reales lo habitual es gestionar estas configuraciones mediante Apps (*también llamadas TAs - Technical Add-ons*). Esto permite mantener el despliegue con una estructura organizada, escalable y fácilmente gestionable a través de un Deployment Server ya que nos permite realizar distribuciones masivas.

### Configurar destino (`outputs.conf`):

```conf
[tcpout]
defaultGroup = default-autolb-group

[tcpout:default-autolb-group]
server = <IP_INDEXER>:9997
```

![Configuración outputs.conf](body/splunk-outputs-conf.webp)

En entornos reales es habitual configurar múltiples indexers para balanceo de carga:

```conf
server = <IP_INDEXER_1>:9997,<IP_INDEXER_2>:9997
```

### Configurar logs a enviar (`inputs.conf`):

```conf
[monitor:///var/log/auth.log]
index = linux
sourcetype = linux_secure
```

![Configuración inputs.conf](body/splunk-inputs-conf.webp)

En sistemas Linux, es habitual que el usuario `splunk` no tenga permisos de lectura sobre algunos logs (como `/var/log/auth.log`).

Una forma rápida de solucionarlo es añadirlo al grupo adecuado:

```bash
sudo usermod -aG adm splunk
```

> En entornos reales, este acceso suele gestionarse de forma más controlada dependiendo de la política de seguridad aplicada.


Una vez aplicados los cambios, basta con reiniciar el forwarder para que empiece a enviar datos:
```bash
sudo systemctl restart SplunkForwarder
```

## Verificación en Splunk

Una vez configurado, puedes entrar en tu instancia de **Splunk Enterprise** a través de WebUI y accede a `Search & Reporting`.  

> http://\<ip_del_servidor\>:8000

Y ejecuta la siguiente búsqueda:

```spl
index=main sourcetype=linux_secure
```

Si todo está correcto, deberías empezar a ver los eventos que se han ingestado.

![Eventos recibidos en Splunk](body/splunk-search-results.webp)

## Troubleshooting básico ##

Si no ves datos en Splunk:

**Verificar conectividad**

```bash
nc -vz <ip_splunk> 9997
```

**Revisar logs del forwarder**
```bash
tail -f /opt/splunkforwarder/var/log/splunk/splunkd.log
```

**Comprobar estado del servicio**
```bash
sudo systemctl status SplunkForwarder
```

Este tipo de comprobaciones son bastante habituales en entornos reales, donde el forwarder puede estar activo pero no enviando datos correctamente.

Por otro lado, si tienes habilitado el arranque con systemd (`enable boot-start`), recuerda que no debes iniciar Splunk con `sudo -u splunk`.

En su lugar, utiliza:

```bash
sudo systemctl start SplunkForwarder
```

## Buenas prácticas

Algunas recomendaciones que aplico desde el inicio:

- Utilizar índices específicos por tipo de dato
- Evitar ingerir logs sin control
- Definir correctamente los sourcetypes
- Documentar las fuentes de datos
- Automatizar despliegues si trabajas con múltiples nodos vía Deployment Server

## Cierre

Con esto ya tienes un flujo completo funcionando:

>**Endpoint → Universal Forwarder → Splunk**


A partir de aquí es donde empieza lo interesante: entender cómo se procesan esos datos, cómo normalizarlos y cómo construir detecciones sobre ellos.

En los próximos artículos iremos entrando en más detalle, tanto a nivel de parsing como de operación diaria en Splunk. Veremos también comandos útiles desde CLI para validar configuraciones, comprobar estados y trabajar de forma más ágil en entornos reales.

Gracias por llegar hasta aquí. Espero que te haya resultado útil. Seguimos.