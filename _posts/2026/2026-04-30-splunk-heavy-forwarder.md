---
title: "Heavy Forwarder en Splunk: cuándo tiene sentido usarlo en entornos reales"
date: "2026-04-30"
categories: [SIEM, Splunk]
tags: [splunk, heavy-forwarder, siem, arquitectura, syslog, ingestion]
media_subpath: /assets/img/posts/2026-04-30-splunk-heavy-forwarder
image:
    path: header/card_heavy_forwarder.webp
    lqip: data:image/webp;base64,UklGRk4AAABXRUJQVlA4IEIAAABQAwCdASoUAAsAPpE6l0eloyIhMAgAsBIJYgCdMoRgABGPuAD+x+x4CVBpYPaN1J/9Js/xNn+Js+SO+8p0vCTiAAA=
published: true
---

## Introducción

En artículos anteriores hemos visto distintas formas de enviar datos hacia Splunk. Primero con **Universal Forwarder**, después viendo arquitecturas de ingestión mediante **Syslog** apoyándonos en colectoras intermedias.

Hasta aquí, el flujo es relativamente sencillo: recibimos eventos y los enviamos hacia indexación.

Pero cuando el entorno empieza a crecer, aparecen nuevas necesidades. Empiezas a necesitar más control sobre qué datos llegan, cómo llegan o incluso decidir qué hacer con ellos antes de enviarlos al indexador.

Ahí es donde empieza a cobrar sentido una pieza bastante habitual en muchas arquitecturas reales con Splunk: el **Heavy Forwarder**.

Y aquí conviene dejar algo claro desde el principio.

Un Heavy Forwarder **no es simplemente un forwarder más grande**.

Su papel dentro de la arquitectura es bastante más interesante: actuar como un punto intermedio donde puedes recibir datos, trabajar con ellos y decidir cómo continuar con su flujo hacia Splunk.

Dicho de una forma sencilla:

> **Un Universal Forwarder transporta datos. Un Heavy Forwarder trabaja con ellos.**

![Flujo Heavy Forwarder](body/splunk-heavy-forwarder-overview.webp)

---

## Qué es realmente un Heavy Forwarder

A nivel técnico, un Heavy Forwarder no deja de ser una instancia completa de **Splunk Enterprise**, utilizada como nodo intermedio dentro del flujo de ingestión.

Esto cambia bastante las cosas, y bastante, además.

Mientras que un Universal Forwarder está pensado para ser ligero y consumir pocos recursos en el endpoint, un Heavy Forwarder está pensado precisamente para asumir trabajo.

Puede recibir datos desde múltiples orígenes, actuar como punto de concentración de eventos y dar bastante más juego a la hora de controlar cómo se van a enviar esos logs aguas abajo.

En muchos casos, termina convirtiéndose en una especie de **colectora inteligente** donde centralizas recepción, organización y bastante parte del control antes de indexar.


## Dónde suele encajar dentro de la arquitectura

En laboratorio solemos montar cosas relativamente simples:

> Origen → Universal Forwarder → Indexer

Y la realidad es que funciona perfectamente.

Pero cuando el entorno empieza a crecer, es bastante habitual encontrarte alguna capa intermedia dentro del flujo de ingestión:

> Origen → Universal Forwarder / Syslog → Heavy Forwarder → Indexer

![Arquitectura con Heavy Forwarder](body/splunk-heavy-forwarder-real-architecture.webp)

Ese nodo intermedio aporta bastante valor.

No solo recibe eventos, también se convierte en un punto intermedio donde puedes controlar mejor qué datos llegan y cómo llegan a Splunk. Al final, cada pieza empieza a tener un papel más claro:

* El origen genera datos.  
* El Heavy Forwarder actúa como punto intermedio de control.  
* El Indexer indexa y almacena.

Y aunque a simple vista parezca añadir complejidad, en entornos grandes suele terminar simplificando bastante la operación diaria.


## Por qué suele utilizarse

Muchas veces no se mete un Heavy Forwarder porque sí. Normalmente aparece porque hay una necesidad real detrás.

A veces necesitas centralizar múltiples fuentes en un único punto. Otras veces quieres separar zonas de red y no exponer directamente los indexers. También puede pasar que quieras tener un nodo intermedio donde controlar mejor el flujo de eventos antes de enviarlos. Y algo bastante habitual: **no todo lo que recibes interesa indexarlo**.

Cuando empiezan a entrar grandes volúmenes de datos, tener un punto donde puedas filtrar, organizar o enrutar mejor la información termina marcando bastante la diferencia.

---

## Un caso bastante habitual: Syslog

Aquí conecta bastante con el artículo anterior.

Cuando trabajas con firewalls, balanceadores, proxys, appliances de seguridad o determinados aplicativos, es bastante común que todo termine llegando a una colectora vía **Syslog**.

Desde ahí, el Heavy Forwarder monitoriza esos archivos y se encarga de enviarlos hacia indexación.

> Dispositivos → Syslog → Heavy Forwarder → Indexer

![Flujo Syslog + Heavy Forwarder](body/splunk-syslog-hf-flow.webp)

Esto aporta varias ventajas.

Por un lado, desacoplas la recepción del dato del indexador final. Por otro, ganas un punto intermedio donde tener bastante más control sobre lo que está ocurriendo.

Y cuando algo falla, tener ese punto de control se nota bastante.

---

## También añade complejidad

No todo son ventajas. Meter un Heavy Forwarder también significa añadir otra pieza a la arquitectura: más recursos, más mantenimiento y otro punto más que vigilar.

Si el entorno es pequeño o simplemente necesitas recoger logs y enviarlos, probablemente no lo necesites.

Muchas veces un flujo sencillo:

> Universal Forwarder → Indexer

es más que suficiente.

Como suele pasar casi siempre, **meter más piezas no siempre significa hacerlo mejor**.

---

## Cuándo empieza a tener sentido

En mi experiencia, es una pieza que empieza a cobrar bastante sentido cuando el entorno deja de ser pequeño y empiezas a necesitar algo más que simple forwarding.

Cuando aparecen múltiples fuentes, segmentación de red, colectoras centralizadas o necesidades de control más fino sobre la ingestión, el Heavy Forwarder suele empezar a encajar bastante bien.

Al final, no deja de ser otra herramienta dentro de Splunk. Lo importante no es meterla porque exista, sino entender cuándo realmente aporta valor.

## Cierre

El Heavy Forwarder es una de esas piezas que empiezas a valorar de verdad cuando sales de laboratorio y empiezas a trabajar con arquitecturas más cercanas a producción.

No destaca por ser ligero ni por ser simple. Destaca porque aporta **control**. Y cuando la plataforma empieza a crecer, disponer de ese punto intermedio suele marcar bastante la diferencia.

Gracias por llegar hasta aquí. 

Espero que te haya resultado útil. 

Seguimos.
