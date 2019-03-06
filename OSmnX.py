# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 10:24:37 2019

@author: Ibrahim
"""

import osmnx as ox
import matplotlib as mpl
mpl.use('WebAgg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#pd.set_option('display.max_columns', 500)
# specify the place name 
place_name= "Uppsala, Uppsala County"


#fetch OSM street network from the location
graph = ox.graph_from_place(place_name,network_type='drive', which_result=2)
graph_map = ox.plot_graph_folium(graph, popup_attribute='name', edge_width=2)
# plot the data 
#fig, ax= ox.plot_graph(graph)

# retrieve footprint of uppsala
area = ox.gdf_from_place(place_name, which_result=2)
#area.plot()

#retreieve building
buildings = ox.buildings_from_address(place_name,distance=2000)
#buildings.plot()

#retrieve resturants from uppsala
restaurants = ox.pois_from_address(place_name,distance=2000, amenities=['restaurant'])
uni = ox.pois_from_address(place_name,distance=2000, amenities=['university'])
hospital =ox.pois_from_address(place_name,distance=2000, amenities=['hospital'])
#covert graph to GeoDataFrame
nodes, edges = ox.graph_to_gdfs(graph)

#plot footprint of uppsala
ax= area.plot(facecolor='black')

#plot the streets on top of the footprint
edges.plot(ax=ax, linewidth= 1, edgecolor='#BC8F8F')

#plot the buildings on top the footprint of uppsala and streets.
buildings.plot (ax=ax, facecolor='w', alpha=0.7)

#plot the resturants on top of the footprint,streets and buildings
restaurants.plot(ax=ax, color='green', alpha=0.7, markersize=10)
uni.plot(ax=ax, color='blue', alpha=0.7, markersize=10)
hospital.plot(ax=ax, color='red', alpha=0.7, markersize=10)
filepath = r"C:\Users\Ibrahim\Documents\interactive_maps\ibra.html"
graph_map.save(filepath)
#red_patch = mpatches.Patch(color='red', label='Hospitals\n wtr lvl con: 2000')
#blue_patch = mpatches.Patch(color='blue', label='Universities\n Wtr lvl con: 1000')
#green_patch = mpatches.Patch(color='green', label='Resturants\n wtr lvl con: 500')

#plt.legend(handles=[red_patch, blue_patch,green_patch],bbox_to_anchor=(1, 0.5), loc="center left")
#plt.tight_layout()
#plt.show()