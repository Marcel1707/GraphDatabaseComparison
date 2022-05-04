from flask import Flask, request
from flask_cors import CORS

from neo4j_client import Neo4JClient

app = Flask(__name__)
CORS(app)

neo4j_client = Neo4JClient(url="neo4j://localhost:7687", auth=("neo4j", "geheim"))

@app.route('/route')
def greet():
    src_lon = request.args.get("src_lon")
    src_lat = request.args.get("src_lat")
    dest_lon = request.args.get("dest_lon")
    dest_lat = request.args.get("dest_lat")

    if src_lon and src_lat and dest_lon and dest_lat:
        success, result = neo4j_client.find_shortest_path(
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


def main():
    try:
        app.run(port=5000)
    finally:
        neo4j_client.close()

if __name__ == '__main__':
    main()