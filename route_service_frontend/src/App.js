import './App.css';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet'
import { Typography, Button, List, ListItem, ListItemText } from '@mui/material';
import React from 'react';
import * as L from "leaflet";

function MapControl(props) {
  useMapEvents({
    click: props.onClick
  })
}

const RouteIcon = L.Icon.extend({
    options: {iconUrl : "https://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|2ecc71&chf=a,s,ee00FFFF" }
});

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: false,
      routeIcon: new RouteIcon(),
      selectingSource: false,
      selectingDestination: false,
      source: undefined,
      destination: undefined,
      result: undefined
    };
  }

  handleMapClick(e) {
    if (this.state.selectingSource) {
      this.setState({ source: e.latlng })
    } else if (this.state.selectingDestination) {
      this.setState({ destination: e.latlng })
    }
  }

  findRoute() {
    if (this.state.loading || !this.state.source || !this.state.destination)
      return

    let src_lon = this.state.source["lng"]
    let src_lat = this.state.source["lat"]
    let dest_lon = this.state.destination["lng"]
    let dest_lat = this.state.destination["lat"]

    let url = `http://localhost:5000/route?src_lon=${src_lon}&src_lat=${src_lat}&dest_lon=${dest_lon}&dest_lat=${dest_lat}`

    this.setState({loading: true})

    fetch(url)
      .then(res => res.json())
      .then(
        (res) => {
          console.log(res)
          this.setState({
            result: res,
            loading: false
          });
        },
        (error) => {
          console.log(error)
          this.setState({
            loading: false
          });
        }
      )
  }

  round(num) {
    return Math.round(num * 100) / 100
  }

  render() {
    return (
      <div className='mainView'>
        <div className='formContainer'>
          <Typography variant="h4">
            Graph Database Comparison
          </Typography>

          <Button variant="outlined" onClick={() => { this.setState({ selectingSource: true, selectingDestination: false }); }}>Select a source point</Button>

          <Button variant="outlined" onClick={() => { this.setState({ selectingSource: false, selectingDestination: true }); }}>Select a destination point</Button>

          <Button variant="contained" disabled={this.state.loading} onClick={() => { this.findRoute() }}>Find route</Button>

          {this.state.result &&
            <div className='result'>
              <Button variant="outlined" onClick={() => { this.setState({ result: undefined }); }}>Reset</Button>

              <Typography variant="h4">
                Path Result
              </Typography>

              <Typography variant="h6">
                Path length: {this.round(this.state.result["path_costs"])} m
              </Typography>

              <Typography variant="h6">
                Search Duration: {this.round(this.state.result["duration"])} s 
              </Typography>

              <Typography variant="h6">
                Source Node
              </Typography>
              <Typography variant="string">
                lat:{this.state.result["source_node"]["latitude"]}<br />lon:{this.state.result["source_node"]["longitude"]}
              </Typography>

              <Typography variant="h6">
                Destination Node
              </Typography>
              <Typography variant="string">
                lat:{this.state.result["destination_node"]["latitude"]}<br />lon:{this.state.result["destination_node"]["longitude"]}
              </Typography>

              <Typography variant="h6">
                Path Nodes
              </Typography>

              <List sx={{
                maxHeight: 400,
              }}>
                {
                  this.state.result["path"].map((node) => {
                    return <ListItem sx={{ padding: 0 }}>
                      <ListItemText primary={JSON.stringify(node)} />
                    </ListItem>
                  })
                }
              </List>

            </div>

          }
        </div>

        <MapContainer center={[48.30201409618453, 14.289276653726965]} zoom={15} scrollWheelZoom={true} onClick={this.handleClick}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {this.state.source &&
            <Marker position={this.state.source}>
            </Marker>
          }

          {this.state.destination &&
            <Marker position={this.state.destination}>
            </Marker>
          }

          {
            this.state.result && this.state.result["path"].map(node => {
              return (
                <Marker position={node} icon={this.state.routeIcon}/>
              )
            })
          }

          <MapControl onClick={this.handleMapClick.bind(this)} />

        </MapContainer>
      </div>

    );
  }
}



export default App;
