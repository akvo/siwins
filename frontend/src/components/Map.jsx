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
import { Modal, Spin, Collapse } from "antd";
import { Column } from "@ant-design/plots";
import { chain, groupBy, orderBy } from "lodash";

const defPos = defaultPos();

const { Panel } = Collapse;

const RenderChart = ({ data }) => {
  // get sample data to find question type
  const sample = data?.[0] || {};
  const qtype = sample?.type;
  data = orderBy(
    data.map((d) => ({
      value: d.value,
      date: d.date?.split(" - ").join("\n"),
    })),
    ["date"],
    "desc"
  );
  let config = {
    data,
    color: "#00b96b",
    // legend: {
    //   position: "top-left",
    // },
  };
  switch (qtype) {
    case "option":
      return null;
    default:
      config = {
        ...config,
        xField: "date",
        yField: "value",
        label: {
          position: "middle",
          // 'top', 'bottom', 'middle',
          style: {
            fill: "#FFFFFF",
            opacity: 0.9,
          },
        },
        xAxis: {
          label: {
            autoHide: true,
            autoRotate: true,
          },
        },
        minColumnWidth: 10,
        maxColumnWidth: 50,
      };
      return <Column {...config} />;
  }
};

const Charts = ({ chartData }) => {
  const [activePanel, setActivePanel] = useState(1);
  const { monitoring } = chartData;
  const grouped = chain(
    groupBy(
      monitoring.filter((d) => d.type === "number"),
      "question"
    )
  ).value();

  return (
    <Collapse
      defaultActiveKey={[activePanel]}
      onChange={setActivePanel}
      accordion={true}
    >
      {Object.keys(grouped).map((key, ki) => {
        return (
          <Panel header={key} key={ki + 1}>
            <RenderChart data={grouped?.[key] || []} />
          </Panel>
        );
      })}
    </Collapse>
  );
};

const Markers = ({ data, getChartData }) => {
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
        eventHandlers={{ click: () => getChartData(id) }}
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
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [chartData, setChartData] = useState(null);

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
    api
      .get(`/data/chart/${id}`)
      .then((res) => {
        setChartData(res.data);
      })
      .catch((e) => console.error(e));
  };

  return (
    <>
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
          {!loading && <Markers data={data} getChartData={getChartData} />}
        </MapContainer>
      </div>

      {/* Chart Modal */}
      <Modal
        title={selectedPoint?.name}
        open={selectedPoint}
        onCancel={() => setSelectedPoint(null)}
        footer={null}
        width={650}
      >
        {!chartData ? (
          <div className="loading-wrapper">
            <Spin />
          </div>
        ) : (
          <Charts chartData={chartData} />
        )}
      </Modal>
    </>
  );
};

export default Map;
