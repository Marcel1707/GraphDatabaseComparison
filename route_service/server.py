import imp
from flask import Flask, request
from flask_cors import CORS

from neo4j_client import Neo4JClient
from tg_client import TigerGraphClient

app = Flask(__name__)
CORS(app)

neo4j_client = Neo4JClient(url="neo4j://localhost:7687", auth=("neo4j", "geheim"))
tg_client = TigerGraphClient(url="http://localhost", username="tigergraph", password="tigergraph")

@app.route('/route')
def find_route():
    src_lon = request.args.get("src_lon")
    src_lat = request.args.get("src_lat")
    dest_lon = request.args.get("dest_lon")
    dest_lat = request.args.get("dest_lat")
    db_service = request.args.get("db_service")

    client = neo4j_client if db_service == "neo4j" else tg_client

    if src_lon and src_lat and dest_lon and dest_lat:
        success, result = client.find_shortest_path(
            source_longitude=src_lon, 
            source_latitude=src_lat, 
            destination_longitude=dest_lon,
            destination_latitude=dest_lat)

        if success:
            return result, 200
        else:
            return result, 400

    else:
        return "Missing parameters!", 400


@app.route('/reset/neo4j')
def reset_neo4j_data():
    neo4j_client.reset_neo4j_data()
    return "Neo4J data has been reset!", 200

@app.route('/reset/tigergraph')
def reset_tigergraph_data():
    tg_client.reset_tg_data()
    return "Tigergraph data has been reset!", 200


def main():
    try:
        app.run(port=5000)
    finally:
        neo4j_client.close()

if __name__ == '__main__':
    main()