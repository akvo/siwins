import React, { useEffect, useState, useRef, useMemo } from "react";
import "leaflet/dist/leaflet.css";
import {
  MapContainer,
  GeoJSON,
  TileLayer,
  CircleMarker,
  Tooltip,
  Marker,
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import { useMapEvents } from "react-leaflet/hooks";
import L, { MarkerCluster } from "leaflet";
import { /*defaultPos,*/ geojson, tileOSM } from "../util/geo-util";
import { api } from "../lib";
import { Modal, Spin, Collapse } from "antd";
import { Column } from "@ant-design/plots";
import { chain, groupBy, orderBy } from "lodash";

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

const Markers = ({ zoom, data, getChartData }) => {
  const [hovered, setHovered] = useState(null);
  const [currentZoom, setCurrentZoom] = useState(zoom);

  const map = useMapEvents({
    zoomend: () => setCurrentZoom(map?._zoom || currentZoom),
  });

  // const rSize = useMemo(() => {
  //   if (currentZoom <= 8) {
  //     return 200;
  //   }
  //   if (currentZoom <= 10) {
  //     return 100;
  //   }
  //   if (currentZoom <= 12) {
  //     return 40;
  //   }
  //   if (currentZoom < 14) {
  //     return 20;
  //   }
  //   if (currentZoom < 16) {
  //     return 4;
  //   }
  //   return 1;
  // }, [currentZoom]);

  data = data.filter((d) => d.geo);
  return data.map(({ id, geo, name }) => {
    const isHovered = id === hovered;
    return (
      <Marker
        key={id}
        position={geo}
        icon={customIcon}
        // pathOptions={{
        //   fillColor: isHovered ? "#FFF" : "#d30808",
        //   color: "#F00",
        //   opacity: 1,
        //   fillOpacity: 1,
        // }}
        // radius={5 * (isHovered ? 2 : 1)}
        // stroke="#fff"
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

// NOTE: iconCreateFunction is running by leaflet, which is not support ES6 arrow func syntax
// eslint-disable-next-line
const createClusterCustomIcon = function (MarkerCluster) {
  return L.divIcon({
    html: `<span>${MarkerCluster.getChildCount()}</span>`,
    className: "custom-marker-cluster",
    iconSize: L.point(33, 33, true),
  });
};

const Map = () => {
  // use tile layer from config
  // const defPos = defaultPos();
  const baseMap = tileOSM;
  const map = useRef();
  const defZoom = 15;
  const defCenter = [-8.68856, 115.494846];
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
            scroll: () => console.log("aaa"),
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
            // <MarkerClusterGroup
            //   onClick={(e) => console.log("onClick", e)}
            //   iconCreateFunction={createClusterCustomIcon}
            //   maxClusterRadius={150}
            //   spiderfyOnMaxZoom={true}
            //   polygonOptions={{
            //     fillColor: "#ffffff",
            //     color: "#f00800",
            //     weight: 5,
            //     opacity: 1,
            //     fillOpacity: 0.8,
            //   }}
            //   showCoverageOnHover={true}
            // >
            <Markers zoom={defZoom} data={data} getChartData={getChartData} />
            // </MarkerClusterGroup>
          )}
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
