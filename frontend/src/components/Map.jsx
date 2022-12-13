import React, { useEffect, useState, useRef } from "react";
import "leaflet/dist/leaflet.css";
import {
  MapContainer,
  GeoJSON,
  TileLayer,
  Tooltip,
  Marker,
} from "react-leaflet";
import L from "leaflet";
import { useMapEvents } from "react-leaflet/hooks";
import { geojson, tileOSM } from "../util/geo-util";
import { api } from "../lib";
import { Modal, Spin } from "antd";
import { Chart } from "./supports";

const Markers = ({ zoom, data, getChartData }) => {
  const [hovered, setHovered] = useState(null);
  const [currentZoom, setCurrentZoom] = useState(zoom);

  const map = useMapEvents({
    zoomend: () => setCurrentZoom(map?._zoom || currentZoom),
  });

  data = data.filter((d) => d.geo);
  return data.map(({ id, geo, name }) => {
    const isHovered = id === hovered;
    console.info(isHovered);
    return (
      <Marker
        key={id}
        position={geo}
        icon={customIcon}
        eventHandlers={{
          click: () => getChartData(id),
          mouseover: () => setHovered(id),
          mouseout: () => setHovered(null),
        }}
      >
        <Tooltip direction="top">{name}</Tooltip>
      </Marker>
    );
  });
};

const customIcon = new L.Icon({
  iconUrl: require("../location.svg").default,
  iconSize: new L.Point(40, 47),
});

const Map = () => {
  // use tile layer from config
  const charts = window.charts;
  const showHistory = window.chart_features.show_history;
  const baseMap = tileOSM;
  const map = useRef();
  const defZoom = 15;
  const defCenter = [-8.68856, 115.494846];
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [activePanel, setActivePanel] = useState(1);

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

  const getChartData = (id) => {
    setSelectedPoint(data.find((d) => d.id === id));
    const qids = charts.map((c) => c.question_id);
    let url = `/data/chart/${id}?history=false`;
    if (showHistory) {
      url = `${url}?history=true`;
    }
    if (qids.length) {
      const queries = qids.map((qid) => `question_ids=${qid}`).join("&");
      url = `${url}&${queries}`;
    }
    api
      .get(url)
      .then((res) => {
        const data = res.data;
        const monitoring = data.monitoring.map((m) => ({
          show_history: showHistory,
          ...m,
        }));
        setChartData({ ...data, monitoring: monitoring });
      })
      .catch((e) => console.error(e));
  };

  const getChartDataWithHistory = (id, question_id) => {
    const url = `/data/chart/${id}?history=true&question_ids=${question_id}`;
    api
      .get(url)
      .then((res) => {
        const currentData = chartData;
        const currentMonitoring = currentData.monitoring.filter(
          (m) => m.question_id !== question_id
        );
        const newMonitoring = res.data.monitoring.map((m) => ({
          show_history: true,
          ...m,
        }));
        setChartData({
          ...currentData,
          monitoring: [...currentMonitoring, ...newMonitoring],
        });
      })
      .catch((e) => console.error(e));
  };

  return (
    <>
      <div className="map-container">
        <MapContainer
          ref={map}
          center={defCenter}
          zoom={defZoom}
          zoomControl={false}
          scrollWheelZoom={true}
          style={{
            height: "100%",
            width: "100%",
          }}
          eventHandlers={{
            scroll: () => {},
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
          {!loading && (
            <Markers zoom={defZoom} data={data} getChartData={getChartData} />
          )}
        </MapContainer>
      </div>

      {/* Chart Modal */}
      <Modal
        title={selectedPoint?.name}
        open={selectedPoint}
        onCancel={() => {
          setSelectedPoint(null);
          setActivePanel(1);
        }}
        footer={null}
        width={650}
        maskClosable={false}
      >
        {!chartData ? (
          <div className="loading-wrapper">
            <Spin />
          </div>
        ) : (
          <Chart
            activePanel={activePanel}
            setActivePanel={setActivePanel}
            chartData={chartData}
            getChartDataWithHistory={getChartDataWithHistory}
          />
        )}
      </Modal>
    </>
  );
};

export default Map;
