import mapnik


def generate_map(zoom, x, y, filename):
    print("Generating map")

    print(mapnik.__file__)

    m = mapnik.Map(256,256) # create a map with a given width and height in pixels
    # note: m.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    # the 'map.srs' is the target projection of the map and can be whatever you wish 
    m.background = mapnik.Color('red') # set background colour to 'steelblue'.  

    s = mapnik.Style() # style object to hold rules
    r = mapnik.Rule() # rule object to hold symbolizers
    # to fill a polygon we create a PolygonSymbolizer
    polygon_symbolizer = mapnik.PolygonSymbolizer()
    polygon_symbolizer.fill = mapnik.Color('#f2eff9')
    r.symbols.append(polygon_symbolizer) # add the symbolizer to the rule object

    # to add outlines to a polygon we create a LineSymbolizer
    line_symbolizer = mapnik.LineSymbolizer()
    line_symbolizer.stroke = mapnik.Color('rgb(50%,50%,50%)')
    line_symbolizer.stroke_width = 0.1
    r.symbols.append(line_symbolizer) # add the symbolizer to the rule object
    s.rules.append(r) # now add the rule to the style and we're done

    m.append_style('My Style',s) # Styles are given names only as they are applied to the map
    ds = mapnik.Shapefile(file='mapnik/110m-admin-0-countries/ne_110m_admin_0_countries.shp')
    print("envelope:", ds.envelope())

    layer = mapnik.Layer('layer_'+zoom) # new layer called 'world' (we could name it anything)
    # note: layer.srs will default to '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
    layer.datasource = ds
    layer.styles.append('My Style')

    m.layers.append(layer)
    m.zoom_all()

    # Write the data to a png image called world.png in the current directory
    mapnik.render_to_file(m,'world.png', 'png')

# Exit the Python interpreter
exit() # or ctrl-d
