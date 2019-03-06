# -*- coding: utf-8 -*-
"""
Created on Mon Feb 18 11:01:20 2019

@author: Ibrahim
"""

from bokeh.plotting import output_file
import numpy as np
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, save
from bokeh.models import HoverTool,GeoJSONDataSource
#from bokeh.tile_providers import CARTODBPOSITRON_RETINA
from bokeh.tile_providers import get_provider, Vendors
import osmnx as ox
import json
import pandas as pd
#pd.options.mode.use_inf_as_na = True
def getXYCoords(geometry, coord_type):
    """ Returns either x or y coordinates from  geometry coordinate sequence. Used with LineString and Polygon geometries."""
    if coord_type == 'x':
        return geometry.coords.xy[0]
    elif coord_type == 'y':
        return geometry.coords.xy[1]

def getPolyCoords(geometry, coord_type):
    """ Returns Coordinates of Polygon using the Exterior of the Polygon."""
    ext = geometry.exterior
    return getXYCoords(ext, coord_type)

def getLineCoords(geometry, coord_type):
    """ Returns Coordinates of Linestring object."""
    return getXYCoords(geometry, coord_type)

def getPointCoords(geometry, coord_type):
    """ Returns Coordinates of Point object."""
    if coord_type == 'x':
        return geometry.x
    elif coord_type == 'y':
        return geometry.y

    
def multiGeomHandler(multi_geometry, coord_type, geom_type):
    """
    Function for handling multi-geometries. Can be MultiPoint, MultiLineString or MultiPolygon.
    Returns a list of coordinates where all parts of Multi-geometries are merged into a single list.
    Individual geometries are separated with np.nan which is how Bokeh wants them.
    # Bokeh documentation regarding the Multi-geometry issues can be found here (it is an open issue)
    # https://github.com/bokeh/bokeh/issues/2321
    """

    for i, part in enumerate(multi_geometry):
        # On the first part of the Multi-geometry initialize the coord_array (np.array)
        if i == 0:
            if geom_type == "MultiPoint":
                coord_arrays = np.append(getPointCoords(part, coord_type), np.nan)
            elif geom_type == "MultiLineString":
                coord_arrays = np.append(getLineCoords(part, coord_type), np.nan)
            elif geom_type == "MultiPolygon":
                coord_arrays = np.append(getPolyCoords(part, coord_type), np.nan)
        else:
            if geom_type == "MultiPoint":
                coord_arrays = np.concatenate([coord_arrays, np.append(getPointCoords(part, coord_type), np.nan)])
            elif geom_type == "MultiLineString":
                coord_arrays = np.concatenate([coord_arrays, np.append(getLineCoords(part, coord_type), np.nan)])
            elif geom_type == "MultiPolygon":
                coord_arrays = np.concatenate([coord_arrays, np.append(getPolyCoords(part, coord_type), np.nan)])

    # Return the coordinates
    return coord_arrays

def getCoords(row, geom_col, coord_type):
    """
    Returns coordinates ('x' or 'y') of a geometry (Point, LineString or Polygon) as a list (if geometry is LineString or Polygon).
    Can handle also MultiGeometries.
    """
    # Get geometry
    geom = row[geom_col]

    # Check the geometry type
    gtype = geom.geom_type

    # "Normal" geometries
    # -------------------

    if gtype == "Point":
        return getPointCoords(geom, coord_type)
    elif gtype == "LineString":
        return list( getLineCoords(geom, coord_type) )
    elif gtype == "Polygon":
        return list( getPolyCoords(geom, coord_type) )

    # Multi geometries
    # ----------------

    else:
        return list( multiGeomHandler(geom, coord_type, gtype) )
    

#pd.set_option('display.max_columns', 50000)
#pd.set_option('display.width', 1000000)

pd.set_option('display.max_columns', 100)  # or 1000
pd.set_option('display.max_rows', 1000)  # or 1000
pd.set_option('display.max_colwidth',100)
pd.set_option('display.width',None)
place= "Uppsala, Uppsala County"

houses = ox.footprints.footprints_from_address(place, footprint_type='building',distance =200, retain_invalid=False)[['geometry']]
#houses= ox.footprints.footprints_from_point([59.858131,17.644621], distance=2000, footprint_type='roof:shape', retain_invalid=False)[['geometry','building']]
#url = r"C:\Users\Ibrahim\.spyder-py3\file_name.json"

#with open(r"C:\Users\Ibrahim\.spyder-py3\file_name.json", 'r') as f:
#    data = json.load(f)
#houses = pd.DataFrame(data)

uni_amenities = ['university']
uni = ox.pois_from_address(place, distance =2000,amenities=uni_amenities)[['geometry',
                                                                              'name',
                                                                              'element_type',
                                                                           ]]



restaurant_amenities = ['restaurant','cafe', 'fast_food']
restaurants = ox.pois_from_address(place, distance =2000, 
                                 amenities=restaurant_amenities)[['geometry', 
                                                                  'name', 
                                                                  'amenity', 
                                                                  'cuisine',                                                 
                                                                 'element_type']]


restaurants = restaurants.to_crs(epsg=3857)
uni = uni.to_crs(epsg=3857)
houses = houses.to_crs(epsg=3857)


restaurants.name.fillna('', inplace=True)
uni.name.fillna('campus', inplace=True)
restaurants.cuisine.fillna('?', inplace=True)


for item in ['way', 'relation']:
   restaurants.loc[restaurants.element_type==item, 'geometry'] = \
   restaurants[restaurants.element_type==item]['geometry'].map(lambda x: x.centroid)                                                                  

for item in ['way', 'relation']:
   uni.loc[uni.element_type==item, 'geometry'] = \
   uni[uni.element_type==item]['geometry'].map(lambda x: x.centroid)     



houses['x'] = houses.apply(getCoords, geom_col='geometry', coord_type='x', axis=1)
houses['y'] = houses.apply(getCoords, geom_col='geometry', coord_type='y', axis=1)

#houses.building.fillna('', inplace=True)
#g_df = houses.drop('geometry', axis=1).copy()
#rdf = houses[['x', 'y']]
#ssource = ColumnDataSource(data=dict({'x': np.array([]), 'y': np.array([])}))
#rdfsource = ColumnDataSource(data=rdf)
geojson = houses.to_json()
geo_source = GeoJSONDataSource(geojson=geojson)
#writeFile =open('file_name.json', 'w')
#writeFile.write(geojson)
#writeFile.close()

#geo_source = GeoJSONDataSource(geojson=houses.to_json())

#houses = building.fillna('')






source = ColumnDataSource(data=dict(
    x=restaurants.geometry.x,
    y=restaurants.geometry.y,
    name=restaurants.name.values,
    cuisine=restaurants.cuisine.values
    ))

Psource = ColumnDataSource(data=dict(
    x=uni.geometry.x,
    y=uni.geometry.y,
    name=uni.name.values


    ))


#gsource = ColumnDataSource(g_df)




TOOLS = "pan,wheel_zoom,reset"
p = figure(title="OSM restaurants", tools=TOOLS, 
           match_aspect=True, x_axis_location=None, y_axis_location=None, 
           active_scroll='wheel_zoom')



tooltips = [
            ('Name', '@name'),('Cuisine', '@cuisine'),('Avg Wtr demand', '21.95539 m3'),
           ]
tooltipss = [
            ('Name', '@name'),('Avg Wtr demand', '50.658 m3')]
tooltipsss = [
            ('building', '@building'),('Avg Wtr demand', '50.658 m3')]


p.grid.grid_line_color = None
ibrahim = get_provider(Vendors.CARTODBPOSITRON)
p.add_tile(ibrahim)


r2=p.circle('x', 'y',color='red', source=source, legend='Resturant',fill_alpha=0.6, size=6)
r3=p.circle('x', 'y', source=Psource, legend='University',fill_alpha=0.6, size=10)
r4=p.patches('x', 'y',color='green', source=geo_source, legend='builings',fill_alpha=0.6)

p.add_tools(HoverTool(renderers=[r2], tooltips= tooltips ))
p.add_tools(HoverTool(renderers=[r3], tooltips=tooltipss))
p.add_tools(HoverTool(renderers=[r4], tooltips=tooltipsss))


outfp= r"C:\Users\Ibrahim\Documents\interactive_maps\omnxRest.html"
save(obj=p, filename=outfp)
