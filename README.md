# landroid using pyworxcloud from MTrab

Landroid-Plugin (proof of concept)

## Table of Content

1. [Generell](#generell)


# Inbetriebnahme
## --------------------------------------
- Im Order "/items" ist eine Beispiel-Item-Datei
- im Ordner "/plugins" ist das komplette Plugin. Diesen in /smarthome/plugins kopieren
- Die Rechte auf den  Plugin + Item Order prüfen und eventuell korrigieren
- Die Einträge in der /etc/plugin.yaml ergänzen
- shNG neu starten
## --------------------------------------


## Generell <a name="generell"/></a>

Die Daten des Plugin müssen in den Ordner /usr/local/smarthome/plugins/landroid/ (wie gewohnt)
Die Rechte entsprechend setzen.

Das Plugin muss in der /etc/plugin.yaml eingefügt werden :

<pre>
<code>
landroid:
    plugin_name: landroid
    class_path: plugins.landroid
    parent_item: worx
    cycle: 120   # Intervall für Update vom Mäher = 120 Sekunden
    landroid_user: XXXXXXXXXXXXXXXXXX
    landroid_pwd:  YYYYYYYYYYYYYYYYYY
</code></pre>

Der Parameter "cycle" ist die Poll-Rate, wie oft die Daten von der IOT-Cloud abgerufen werden sollen.
User und PWD sind im Klartext zu hinterlegen.
Das "parent"-item ist für die vordefinierten Structs.

Im Ordner /items muss eine Item-Datei mit folgendem Inhalt erstellt werden (landroid.yaml).
Die items werden über structs aus der plugin.yaml des plugins erstellt.
<pre>
<code>
%YAML 1.1
---
worx:
    struct: landroid.child
</code></pre>

**Falls ein anderer Name für das parent-Item genutzt werden soll, muss dieser
in der /etc/plugin.yaml gleichlautend zum Eintrag in der /items/landroid.yaml eingetragen werden**
