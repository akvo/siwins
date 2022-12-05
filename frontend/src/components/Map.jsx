import React, { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import {
  MapContainer,
  GeoJSON,
  TileLayer,
  Circle,
  Tooltip,
} from "react-leaflet";
import { defaultPos, geojson, tileOSM } from "../util/geo-util";
import { api } from "../lib";

const defPos = defaultPos();

const Markers = ({ data }) => {
  data = data.filter((d) => d.geo);
  return data.map(({ id, geo, name }) => {
    const hovered = false;
    const fill = "#F00";
    const r = 3;
    const stroke = "#fff";
    return (
      <Circle
        key={id}
        center={geo}
        pathOptions={{
          fillColor: hovered ? "#FFF" : fill,
          color: fill,
          opacity: 1,
          fillOpacity: 1,
        }}
        radius={r * (hovered ? 3 : 1)}
        stroke={stroke}
      >
        <Tooltip direction="top">{name}</Tooltip>
      </Circle>
    );
  });
};

const Map = () => {
  // use tile layer from config
  const baseMap = tileOSM;
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);

  useEffect(() => {
    setLoading(true);
    api
      .get("/data/maps")
      .then((res) => {
        setData(res.data);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="map-container">
      <MapContainer
        bounds={defPos.bbox}
        zoomControl={false}
        scrollWheelZoom={true}
        style={{
          height: "100%",
          width: "100%",
        }}
      >
        <TileLayer {...baseMap} />
        <GeoJSON
          key="geodata"
          style={{
            weight: 1,
            fillColor: "#00989f",
            fillOpacity: 0.25,
            opacity: 0.25,
            color: "#FFF",
          }}
          data={geojson}
        />
        {!loading && <Markers data={data} />}
      </MapContainer>
    </div>
  );
};

export default Map;
