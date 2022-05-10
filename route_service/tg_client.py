import pyTigerGraph as tg
import pandas as pd
import json
import time

class TigerGraphClient:
    def __init__(self, url, username, password):
        self.password = password
        self.username = username
        self.url = url
        self.establish_connection()

    def establish_connection(self):
        print("CONNECTING...")
        self.conn = tg.TigerGraphConnection(host=self.url, restppPort=9000, gsPort=14240, username=self.username, password=self.password)
        print(self.conn)

    def create_graph_schema(self):
        print("CREATING SCHEMA...")
        self.execute_tigergraph_query('''
            USE GLOBAL
            CREATE VERTEX Node (PRIMARY_ID id INT, lat DOUBLE, lon DOUBLE) WITH primary_id_as_attribute="true"
            CREATE DIRECTED EDGE Road (From Node, To Node, length DOUBLE) WITH REVERSE_EDGE="Reverse_Road"
        ''')

    def create_graph(self,graphname):
        print("CREATING GRAPH...")
        self.execute_tigergraph_query(f'CREATE GRAPH {graphname}(Node, Road, Reverse_Road)')
        self.conn.graphname=graphname
        secret = self.conn.createSecret()
        authToken = self.conn.getToken(secret)
        authToken = authToken[0]
        self.conn = tg.TigerGraphConnection(host=self.url, graphname=graphname, username=self.username, password=self.password, apiToken=authToken)

    def load_data(self):
        self.insert_vertices("../graph_downloader/results/nodes.csv")
        self.insert_edges("../graph_downloader/results/edges.csv")

    def reset_tg_data(self):
        self.establish_connection()
        self.drop_all()
        self.create_graph_schema()
        self.create_graph(graphname = "myGraph")
        self.load_data()
        self.install_required_queries()


    def insert_vertices(self, data_file):
        print("INSERTING VERTICES...")

        self.execute_tigergraph_query('''
            USE GRAPH myGraph
            BEGIN
            CREATE LOADING JOB load_job_nodes FOR GRAPH myGraph {
                DEFINE FILENAME MyDataSource;
                LOAD MyDataSource TO VERTEX Node VALUES($0, $1, $2) USING SEPARATOR=",", HEADER="true", EOL="\n";
                }
            END
        ''')

        result = self.conn.uploadFile(data_file, fileTag='MyDataSource', jobName='load_job_nodes', sep=",")
        print(json.dumps(result, indent=2))

    def insert_edges(self, data_file):
        print("INSERTING EDGES...")

        self.execute_tigergraph_query('''
            USE GRAPH myGraph
            BEGIN
            CREATE LOADING JOB load_job_edges FOR GRAPH myGraph {
                DEFINE FILENAME MyDataSource;
                LOAD MyDataSource TO EDGE Road VALUES($1, $2, $0) USING SEPARATOR=",", HEADER="true", EOL="\n", QUOTE="double";
                }
            END
        ''')

        result = self.conn.uploadFile(data_file, fileTag='MyDataSource', jobName='load_job_edges', sep=",")
        print(json.dumps(result, indent=2))

        

    def execute_tigergraph_query(self, query):
        result = self.conn.gsql(query)
        #print(result)
        return result

    def install_required_queries(self):
        # create find nearest node query
        with open('tg_gsql_queries/find-nearest-node-query.gsql') as f:
            query = f.read()
            self.execute_tigergraph_query(query)
        
        # create a star query
        with open('tg_gsql_queries/a-star-query.gsql') as f:
            query = f.read()
            self.execute_tigergraph_query(query)

    def find_nearest_node(self, longitude, latitude, search_distance = 1):
        result = self.execute_tigergraph_query(f"""
            BEGIN
                RUN QUERY find_nearest_node({longitude}, {latitude}, {search_distance})
            END
        """)

        json_result = json.loads(result)
        node = json_result["results"][0]["filtered_nodes"][0]
        
        return {"id":node["v_id"], "latitude":node["attributes"]["lat"], "longitude":node["attributes"]["lon"]}

    
    def perform_a_star_shortest_path(self, src_node_id, dest_node_id):
        result = self.execute_tigergraph_query(f'''
            BEGIN
                RUN QUERY tg_astar(({src_node_id},"Node"), ({dest_node_id},"Node"), ["Road"], "DOUBLE", "lat" , "lon", "length")
            END
        ''')
    
        data = json.loads(result)

        node_attr = [node["attributes"] for node in data["results"][0]["path"]]

        path_costs = data["results"][0]["@@sum_total_dist"]
        path = [{"lat": node["lat"], "lon": node["lon"]} for node in node_attr]

        return path, path_costs


    def find_shortest_path(self, source_longitude, source_latitude, destination_longitude, destination_latitude):

        self.execute_tigergraph_query('USE GRAPH myGraph')
        start_time = time.time()

        try:
            source_node = self.find_nearest_node(source_longitude, source_latitude)
            print(source_node)
            destination_node = self.find_nearest_node(destination_longitude, destination_latitude)
            path, path_costs = self.perform_a_star_shortest_path(source_node["id"], destination_node["id"])
        except Exception as e:
            return False, str(e)
       
        duration = time.time() - start_time


        return True, { "path": path, "path_costs": path_costs, "source_node": source_node, "destination_node": destination_node, "duration":duration }

  
    def drop_all(self):
        print("DROPPING ALL...")
        result = self.execute_tigergraph_query('''USE GLOBAL DROP ALL''')
        return result