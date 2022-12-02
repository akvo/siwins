import React from "react";
import "leaflet/dist/leaflet.css";
import { MapContainer, GeoJSON, TileLayer } from "react-leaflet";
import { defaultPos, geojson, tileOSM } from "../util/geo-util";

const defPos = defaultPos();

const Map = () => {
  // use tile layer from config
  const baseMap = tileOSM;

  return (
    <div className="map-container">
      <MapContainer
        bounds={defPos.bbox}
        zoomControl={false}
        scrollWheelZoom={false}
        style={{
          height: "100%",
          width: "100%",
        }}
      >
        <TileLayer {...baseMap} />
        <GeoJSON
          key="geodata"
          style={{
            weight: 2,
            fillColor: "#00989f",
            fillOpacity: 0.5,
            opacity: 0.5,
            color: "#FFF",
          }}
          data={geojson}
        />
      </MapContainer>
    </div>
  );
};

export default Map;
