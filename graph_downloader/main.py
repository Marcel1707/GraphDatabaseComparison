from pyrosm import OSM, get_data
import csv
import os

osm = OSM(get_data("Linz"))
#osm = OSM(get_data("test_pbf"))

nodes, edges = osm.get_network(nodes=True, network_type="driving")

nodes_header = ["id", "lat", "lon"]
nodes_data = []
for index, row in nodes.iterrows():
    nodes_data.append([row["id"], row["lat"], row["lon"]])
    
edges_header = ["name", "maxspeed", "length", "node1", "node2", "oneway"]
edges_data = []
for index, row in edges.iterrows():
    edges_data.append([row["name"], row["maxspeed"], row["length"], row["u"], row["v"], row["oneway"]])


with open("results/nodes.csv", "w", newline="") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(nodes_header)
    writer.writerows(nodes_data)

with open("results/edges.csv", "w", newline="") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(edges_header)
    writer.writerows(edges_data)


