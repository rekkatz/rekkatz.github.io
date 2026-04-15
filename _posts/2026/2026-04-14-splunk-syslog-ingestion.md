---
title: "Ingestión de logs en Splunk mediante Syslog: gestión en entornos reales"
date: "2026-04-14"
categories: [SIEM, Splunk]
tags: [splunk, syslog, rsyslog, ingestion, siem, heavy-forwarder]
media_subpath: /assets/img/posts/2026-04-14-splunk-syslog-ingestion
image:
   path: header/card_splunk_syslog_ingestion.webp
   lqip: data:image/webp;base64,UklGRk4AAABXRUJQVlA4IEIAAADwAgCdASoUAAsAPpE6l0eloyIhMAgAsBIJYgCw7DDpkAD+tNV+tRQH1/8EDKd/9QZ//pNn/9QZ+fr95MWid8K34AA=
published: true
---

## Introducción

En el artículo anterior vimos cómo enviar logs a Splunk utilizando un agente llamado Universal Forwarder. Ese es uno de los métodos más habituales que se suele utilizar, pero no es el único.

Cuando empiezas a trabajar con entornos un poco más reales, sobre todo con dispositivos de red o herramientas de seguridad, te das cuenta de que no siempre puedes instalar un agente. En esos casos, lo normal es que los logs se envíen mediante **Syslog**.

Aquí no voy a entrar en la configuración paso a paso como si hemos visto en anteriores artículos. Lo interesante es entender cómo se suele montar esta arquitectura en entornos reales y por qué se toman ciertas decisiones desde el principio.


## ¿Qué es Syslog y por qué se usa?

`Syslog` es un protocolo muy extendido que permite enviar eventos desde un sistema a otro a través de la red. Es, básicamente una forma estándar de enviar logs entre sistemas.

Es habitual encontrarlo en:

- Firewalls  
- Switches y routers  
- Sistemas Linux  
- Herramientas de seguridad  

A diferencia del Universal Forwarder, aquí no hay un agente que controle el envío. El sistema origen simplemente envía los eventos a una IP y a un puerto. Eso hace que sea muy fácil de integrar, pero también implica **perder cierto control sobre los datos desde el origen**.

> Es importante diferenciar entre el protocolo y la herramienta. **Syslog como protocolo** define cómo viajan los eventos, pero luego necesitas herramientas como **`rsyslog`** o **`syslog-ng`** para recibirlos y gestionarlos en el sistema.

### TCP vs UDP en Syslog

Uno de los primeros puntos donde empiezan las decisiones reales, es en el tipo de transporte que vamos a utilizar para enviar los datos.

Syslog puede funcionar tanto sobre **UDP como sobre TCP**, y la elección tiene **bastante impacto real en la ingestión**. A nivel teórico es sencillo, pero en la práctica cambia bastante el comportamiento entre elegir uno u otro.

- **UDP**
  - Más rápido y ligero  
  - No garantiza la entrega  
  - Puede haber pérdida de eventos  

- **TCP**
  - Garantiza la entrega de los datos  
  - Evita pérdida o truncado de eventos  
  - Mayor consumo de recursos en la colectora  

En entornos donde es importante **asegurar la integridad de los logs**, lo habitual es utilizar TCP, aunque implique más carga en la infraestructura.

Aun así, no todos los entornos tienen el mismo nivel de exigencia. En algunos casos, sobre todo cuando el volumen es muy alto, se trabaja con UDP asumiendo cierta pérdida de eventos como algo aceptable.

Esto suele depender de los requisitos del cliente y del tipo de datos que se estén enviando.

### Puertos y configuración real

Otro detalle que cambia bastante entre laboratorio y producción es el uso de puertos utilizados.

Aunque tradicionalmente Syslog utiliza el puerto **514 por defecto**, en entornos reales rara vez se deja tal cual con dicho puerto.

Es bastante común configurar **puertos de rango alto** (por ejemplo, `20000`, `20514`, etc.), tanto en UDP como en TCP, en función de cómo esté diseñada la colectora y de las necesidades del entorno.

Esto permite, sobre todo:

- Evitar conflictos con servicios por defecto.
- Tener mayor control sobre el tráfico.
- Adaptarse a políticas de red del cliente  

En este tipo de configuraciones, los dispositivos origen se ajustan para enviar los eventos al puerto definido en la colectora.

Todo esto hace que, aunque Syslog sea sencillo a nivel conceptual, en la práctica tenga bastantes decisiones detrás que impactan directamente en la calidad de los datos que llegan a Splunk.

Esto suele venir condicionado por temas de firewall, segmentación de red o simplemente por organización interna. Además, permite separar mejor los flujos de datos desde el inicio.


## ¿Por qué no enviar directamente a Splunk?

Cuando empiezas, lo más sencillo es enviar directamente desde el dispositivo de origen a Splunk. Funciona, es rápido y te permite ver datos enseguida...

**Dispositivo → Splunk**

En laboratorio funciona, pero en cuanto el entorno crece, también empiezan a aparecer los problemas.

Por ejemplo, empiezan a aparecer problemas como:

* No tienes control sobre cuánto dato entra
* No puedes filtrar fácilmente en origen
* El indexador se convierte en punto de entrada directo
* Si algo falla, es más difícil de aislar

Otro punto importante es la **gestión de fallos**.

Si los dispositivos envían directamente a Splunk, una caída del servicio puede provocar la **pérdida de eventos**, especialmente cuando se utiliza UDP.

En arquitecturas donde se utiliza una colectora, es habitual almacenar los logs en local antes de que sean procesados por el Heavy Forwarder. Esto permite **evitar la pérdida de datos** ante caídas temporales del sistema.

Por eso, en entornos reales, el enfoque de enviar directamente desde **Dispositivo → Splunk** se intenta evitar siempre que sea posible.

## Cómo se suele montar en la práctica

Lo habitual es introducir una capa intermedia entre las fuentes de datos y Splunk.

El flujo más común suele ser algo así:

![Arquitectura Syslog en Splunk](body/splunk-syslog-architecture.webp)

Vamos por partes.


### Envío desde origen: no siempre es directo

Otro punto interesante es que, en muchos entornos, las fuentes de datos ni siquiera envían directamente a la colectora.

Lo que se suele hacer es utilizar un gestor de syslog en origen, donde apuntan varias máquinas. Desde ahí, se centraliza el envío hacia la colectora.

Esto ayuda a reducir el tráfico en red, simplifica la gestión y permite tener un punto de control antes de que los datos salgan hacia Splunk.


## La colectora: punto central

![Flujo de datos para ingestión](body/splunk-syslog-collector-flow.webp)

La **colectora** es una máquina que se encarga de recibir todos los logs vía Syslog, es donde realmente empieza a tener sentido todo esto.

En lugar de que cada dispositivo hable directamente con Splunk, todos envían sus eventos a esta máquina  a través de herramientas como **`rsyslog`** o **`syslog-ng`**, que se encargan de recibirlos y almacenarlos en local.

Normalmente aquí se suele utilizar `rsyslog` o similar, entiendo que según preferencia o distribución utilizada, esto nos permite cosas clave como:

* Escuchar en el puerto de syslog (514 por defecto o configurado para cada cliente/eventos según aplicativo)
* Recibir eventos de múltiples fuentes
* Guardarlos en ficheros locales

Esto ya te da algo importante: **centralización y control**.


### Organización de la ingestión

En la práctica, la colectora no se suele configurar de forma genérica para todo.

Lo normal es ir separando según el cliente, la fuente de datos o el tipo de eventos que quieres recibir.

Por ejemplo, si un cliente quiere integrar varios sistemas en Splunk, lo habitual es crear configuraciones específicas (`.conf`) para cada caso. Esto suele ir acompañado de puertos diferentes para cada flujo de datos, en lugar de meter todo en el mismo y luego intentar filtrarlo.

Desde ahí puedes jugar un poco más con el control de los eventos:

- Filtrar por tipo de log o *facility*  
- Separar por origen (host, aplicación, etc.)  
- Organizar mejor cómo llegan los datos desde el principio  

En algunos casos también se pueden hacer pequeñas modificaciones sobre los logs, aunque normalmente se intenta evitar y dejar ese trabajo para fases posteriores.

Al final, lo que buscas con esto es **tener control desde el inicio de la ingestión**. Cuando empiezan a entrar muchas fuentes distintas, si no estructuras bien la ingestión, luego todo se complica bastante más.


## El papel del Heavy Forwarder

Una vez los logs están en la colectora, entra en juego el **Heavy Forwarder (HF)**.

Este forwarder no es como el UF que vimos antes. Tiene más capacidad, y sobre todo, más control sobre los datos.

Desde aquí se puede:

* Leer los ficheros generados por syslog
* Filtrar eventos
* Aplicar cierto preprocesado
* Enviar los datos hacia los indexers

Esto permite **decidir qué datos llegan realmente a Splunk** y cómo lo hacen. 

A diferencia del Universal Forwarder, aquí tienes más margen para decidir qué hacer con los datos antes de que lleguen a Splunk. Eso es lo que te permite mantener cierto orden cuando el volumen empieza a crecer.


## Por qué esta arquitectura tiene sentido

Aunque al principio parezca más compleja, esta forma de trabajar tiene bastante lógica.

Cada componente tiene su función y permite separar responsabilidades:

* El origen solo envía logs
* La colectora recibe y organiza
* El HF controla y envía
* Splunk indexa y permite buscar

Este tipo de diseño **no es casual**. Es lo que hace que Splunk pueda escalar y seguir siendo manejable cuando el entorno crece.

Y sobre todo, evita depender directamente del indexador para todo.


## Cosas que suelen marcar la diferencia

Con el tiempo, hay ciertos puntos que se repiten bastante:

* No enviar todo “tal cual” desde origen
* Tener claro qué datos quieres ingerir
* Centralizar siempre que sea posible
* Evitar exponer directamente Splunk a dispositivos externos

Muchas veces los problemas **no vienen de Splunk** en sí, sino de cómo se ha planteado la ingestión desde el principio.


## Relación con lo que viene después

Todo esto es solo la primera parte del camino.

Una vez que los datos llegan a Splunk, todavía queda lo más importante:

* Entender cómo se procesan
* Cómo se parsean correctamente
* Cómo darles sentido para detección

Si la base de ingestión no está bien planteada, todo lo demás se complica bastante.


## Cierre

El uso de Syslog en Splunk no es solo una alternativa al Universal Forwarder, sino una pieza clave en muchas arquitecturas reales que te puedes encontrar.

Al final, todo esto no deja de ser la forma en la que se suelen montar este tipo de integraciones en entornos reales.

Son configuraciones con las que me he ido encontrando **en el día a día como integrador**, y que con el tiempo acabas aplicando casi por inercia cuando el entorno empieza a crecer.

Entender este flujo y por qué se monta así ayuda mucho más que simplemente saber configurarlo.

Gracias por llegar hasta aquí. Espero que te haya resultado útil. Seguimos.