#!/usr/bin/env python
import mapnik
#stylesheet = 'mapnik/world_style.xml'
stylesheet = 'mapnik/denmark.xml'
stylesheet = 'mapnik/simple.xml'
image = 'denmark.png'
m = mapnik.Map(256, 256)
mapnik.load_map(m, stylesheet)
m.zoom_all() 
mapnik.render_to_file(m, image)
print (f"rendered image to {image}")

