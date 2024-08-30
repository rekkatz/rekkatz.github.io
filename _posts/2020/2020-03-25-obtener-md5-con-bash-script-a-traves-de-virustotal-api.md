---
title: "Obtener MD5 a través de Virustotal API"
date: "2020-03-25"
categories: [Scripts]
tags: [Scripts, Virustotal, API, Blue-Team]
media_subpath: /assets/img/posts/2020-03-25-obtener-md5-con-bash-script-a-traves-de-virustotal-api
image:
   path: header/portada_apivirustotal.webp
   lqip: data:image/webp;base64,UklGRl4AAABXRUJQVlA4IFIAAABwAwCdASoUAAsAPzmEuVOvKKWisAgB4CcJYwAAXgj4MU/6d1gA/tWkP5TCRxApF4PbigHzYz1hM8rFdLfaaqqwEHKBSIJ2feDhQpZEnFLIKoQA
   
published: true
---

¡Hola compañeros!

Este va a ser un artículo rapido y conciso. 

En una solución Cloud de Endpoint necesitaba añadir 500 IOC's en formato hash para bloquear, esta consola solo permitía añadir el hash en formato MD5 y el cliente nos había proporcionado una lista con 500 hashes en varios formatos (MD5, SHA-1 y SHA-256).

Podemos tomar varias opciones...indicar al cliente que nos pase los 500 hashes en formato MD5 o pensar la forma en la cual podemos tomar esos hashes ¿?... bingo, _**API Virustotal**_.

La API gratuita nos permite realizar 4 peticiones/minuto y un máximo de 1000/día, por lo tanto en el código le he metido un sleep de 15 segundos entre cada petición para completar el minuto.

### Código del Script

```bash
#!/usr/bin/env bash

FILE=$1
API="---API---"
count=0

touch ./result_hash.txt
echo "Number,SourceHash,VTHits,MD5hash" > ./result_hash.txt

echo "Processing..."

while IFS= read -r line || [ -n "$line" ]; do

    let count=count+1
    var=$(curl -s -X POST 'https://www.virustotal.com/vtapi/v2/file/report' --form apikey="$API" --form resource="$line" | awk -F'positives\":' '{print $2}' | awk -F' ' '{print $1$5}' | sed 's/["}]//g')

    if [ -z "$var" ]; then
        echo "$count,$line,NULL,NULL" >> ./result_hash.txt
        echo "Hash $count - Not Found!"
    else
        echo "$count,$line,$var" >> ./result_hash.txt
        echo "Hash $count - OK!"
    fi

    sleep 15
done < $FILE
```

El script en si es sencillo y puede que tenga algún error que otro, pero el resultado es el esperado.

Metemos el archivo que contiene los hashes como argumento, separando cada hash por línea.

![](body/post8-image1.png)

Sintaxis de ejecución:

```shell
./vthash.sh <FILE_HASHES>
```

### Output del Script

![](body/post8-image2.png)

Se creará un archivo _**result\_hash.txt**_ en el mismo directorio, este contiene el resultado.

Como podéis ver, los hashes que no se encuentren en la BBDD de **Virustotal** no saldrán...lógica, por lo tanto he añadido NULL en el caso de que la variable VAR se encuentre vacía.

Este código no solo sirve para obtener los hashes en formato MD5, si modificás los AWK podéis obtener una lista de cualquier cadena del resultado de la petición a VT con el comando CURL.

### Resultado Final

![](body/post8-image3.png)

Para resumir y finalizar, el caso es que tuve que pedirle al cliente 49 hashes que no fueron encontrados en la BBDD, pero 49 de 509 no está mal ¿no?.

Dejo mi **Github** con el script por si lo necesitáis:

> [Github - Getmd5virustotal](https://github.com/rekkatz/getmd5virustotal)

Espero que os pueda servir de ayuda y como digo siempre, cualquier duda, sugerencia, etc, la podéis dejar en los comentarios.

Nos vemos en el próximo artículo.

Saludos!
