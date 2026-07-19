---
title: "SOC Weekly #{{ edition }} | Vulnerabilidades críticas de la semana ({{ period }})"
date: "{{ publication_date }}"
categories: [Threat Intelligence, Vulnerabilidades]
tags: [CVE, CISA KEV, Splunk, SIEM, Detection Engineering, Threat Intelligence, SOC]
media_subpath: /assets/img/posts/{{ media_directory }}
image:
   path: header/card_soc_weekly_{{ edition_padded }}.webp

published: false
---

# SOC Weekly #{{ edition }} | Vulnerabilidades críticas de la semana

## Resumen ejecutivo

{{ executive_summary }}

> Esta edición prioriza vulnerabilidades con explotación activa, presencia en CISA KEV o impacto significativo sobre tecnologías empresariales.

## Resumen rápido

| Indicador | Valor |
|---|---:|
| Vulnerabilidades analizadas | {{ vulnerability_count }} |
| Explotación activa | {{ exploited_count }} |
| Incluidas en CISA KEV | {{ kev_count }} |
| Ejecución remota de código | {{ rce_count }} |
| Periodo analizado | {{ period }} |

## Prioridad de actuación

{{ priority_table }}

## Vulnerabilidad destacada de la semana

{{ featured_vulnerability }}

## Otras vulnerabilidades relevantes

{{ vulnerability_sections }}

## Splunk Detection Corner

{{ splunk_detection_corner }}

> Las búsquedas SPL incluidas son orientativas y deben adaptarse a los índices, sourcetypes, campos y normalización CIM disponibles en cada entorno.

## Qué debería revisar un SOC esta semana

{{ soc_checklist }}

## Recomendaciones para administradores

{{ administrator_recommendations }}

## Referencias oficiales

{{ references }}

## Conclusión

{{ conclusion }}
