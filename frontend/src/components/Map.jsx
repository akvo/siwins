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
import { CloseCircleOutlined } from "@ant-design/icons";
import { generateAdvanceFilterURL } from "../util/utils";
import { UIState } from "../state/ui";

const Markers = ({ zoom, data, getChartData, getRegistrationData }) => {
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
          click: () => {
            getChartData(id);
            getRegistrationData(id);
          },
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
  const { advanceSearchValue } = UIState.useState((s) => s);
  const baseMap = tileOSM;
  const map = useRef();
  const defZoom = 9;
  const defCenter = [-8.670677602749869, 115.21310410475814];
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [registrationData, setRegistrationData] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [activePanel, setActivePanel] = useState(1);

  useEffect(() => {
    setLoading(true);
    let url = `data/maps`;
    url = generateAdvanceFilterURL(advanceSearchValue, url);
    api
      .get(url)
      .then((res) => {
        setData(res.data);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [advanceSearchValue]);

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

  console.log(chartData);

  const getRegistrationData = (id) => {
    setSelectedPoint(data.find((d) => d.id === id));
    const url = `/data/${id}?history=false`;
    api
      .get(url)
      .then((res) => {
        const data = res.data;
        setRegistrationData(data?.registration_data);
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
      <div id="map-view">
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
              <Markers
                zoom={defZoom}
                data={data}
                getChartData={getChartData}
                getRegistrationData={getRegistrationData}
              />
            )}
          </MapContainer>
        </div>

        {/* Chart Modal */}
        <Modal
          title={
            <>
              <div className="title-holder">
                <p>{selectedPoint?.name}</p>
                <CloseCircleOutlined
                  onClick={() => {
                    setSelectedPoint(null);
                    setActivePanel(1);
                  }}
                />
              </div>
            </>
          }
          open={selectedPoint}
          onCancel={() => {
            setSelectedPoint(null);
            setActivePanel(1);
          }}
          closable={false}
          footer={null}
          width={650}
          maskClosable={false}
          className="detail-modal"
        >
          {!chartData ? (
            <div className="loading-wrapper">
              <Spin />
            </div>
          ) : (
            <>
              <RegistrationDetail data={registrationData} />
              <Chart type={"BAR"} data={[400, 300, 350, 200, 280]} />
            </>
          )}
        </Modal>
      </div>
    </>
  );
};

const RegistrationDetail = ({ data }) => {
  return (
    <div className="registration-table">
      {data?.map((detail) => (
        <div className="registration-row" key={detail.question}>
          <div className="registration-question">{detail.question}:</div>
          <div className="registration-answer">{detail.answer}</div>
        </div>
      ))}
    </div>
  );
};

export default Map;
