from neo4j import GraphDatabase
import pandas as pd
import time

class Neo4JClient:
    def __init__(self, url, auth):
        self.url = url
        self.auth = auth

        self.driver = GraphDatabase.driver(url, auth=auth)
        self.session = self.driver.session()


    def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
        results_dir = "graph_downloader/results/"
        edges = pd.read_csv(results_dir + "edges.csv")
        nodes = pd.read_csv(results_dir + "nodes.csv")
        return nodes, edges


    def execute_query(self, statement: str, parameters = None):
        print("executing", statement)

        result = self.session.run(statement, parameters)
        for line in result:
            print(line)
        print()

        return list(result)


    def add_data_to_neo4j(self, nodes, edges):
        batch_size = 100000

        # clear database
        self.execute_query(f""" 
            MATCH (n)
            CALL {{
                WITH n
                DETACH DELETE n
            }} IN TRANSACTIONS of {batch_size} ROWS;
        """)


        # add nodes
        self.execute_query(f""" 
            UNWIND $records AS row
            CALL {{
                WITH row
                CREATE (n:Node {{id: row.id, longitude: row.lon, latitude: row.lat}})
            }} IN TRANSACTIONS of {batch_size} ROWS;
        """, parameters={'records':nodes.to_dict('records')})


        # add index on node id
        self.execute_query("""
            CREATE INDEX node_id IF NOT EXISTS
            FOR (n:Node)
            ON (n.id)
        """)

        # add edges
        self.execute_query(f""" 
            UNWIND $records AS row
            CALL {{
                WITH row
                MATCH (node1:Node {{id: row.node1}}), (node2:Node {{id: row.node2}})
                CREATE (node1) - [r:ROAD {{length: toFloat(row.length)}}] -> (node2)
            }} IN TRANSACTIONS of {batch_size} ROWS;
        """, parameters={'records':edges.to_dict('records')})


    def find_nearest_node_query(self, longitude, latitude, node_name, search_distance = 1000):
        return f"""
            CALL {{
                MATCH ({node_name}:Node) 
                WITH {node_name}, point.distance(point({{longitude:{node_name}.longitude, latitude:{node_name}.latitude}}), point({{longitude:{longitude}, latitude:{latitude}}})) AS dist
                WHERE dist <= {search_distance}
                RETURN {node_name}
                ORDER BY dist ASC
                LIMIT 1
            }}
        """
        

    def find_shortest_path(self, source_longitude, source_latitude, destination_longitude, destination_latitude):
        query = f"""
            {self.find_nearest_node_query(source_longitude, source_latitude, "source")}
            WITH source
            {self.find_nearest_node_query(destination_longitude, destination_latitude, "destination")}
            WITH source, destination
            CALL apoc.algo.aStar (source, destination, 'ROAD', 'length', 'latitude', 'longitude')
            YIELD path, weight as costs
            RETURN path, costs, source, destination
        """

        start_time = time.time()

        try:
            path_result = self.session.run(query).single().data()
        except Exception as e:
            return False, str(e)

        duration = time.time() - start_time

        route = []
        for route_element in path_result["path"]:
            if type(route_element) is dict:
                route.append({"lat": route_element["latitude"], "lon": route_element["longitude"]})

        return True, { "path": route, "path_costs": path_result["costs"], "source_node": path_result["source"], "destination_node": path_result["destination"], "duration":duration }

    def close(self):
        self.session.close()
        self.driver.close()

