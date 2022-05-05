from pyrosm import OSM, get_data
import csv

print("Starting to convert nodes and edges...")

osm = OSM(get_data("Linz"))
#osm = OSM(get_data("test_pbf"))

nodes, edges = osm.get_network(nodes=True, network_type="driving")

nodes_header = ["id", "lat", "lon"]

with open("results/nodes.csv", "w", newline="") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(nodes_header)

    for index, row in nodes.iterrows():
        writer.writerow([row["id"], row["lat"], row["lon"]])
    
edges_header = ["length", "node1", "node2"]

with open("results/edges.csv", "w", newline="") as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(edges_header)

    for index, row in edges.iterrows():
        writer.writerow([row["length"], row["u"], row["v"]])
        if not row["oneway"]:
            writer.writerow([row["length"], row["v"], row["u"]])


