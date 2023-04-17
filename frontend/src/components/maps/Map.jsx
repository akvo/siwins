import React, { useEffect, useState, useRef, useCallback } from "react";
import "./style.scss";
import "leaflet/dist/leaflet.css";
import {
  MapContainer,
  GeoJSON,
  TileLayer,
  Tooltip,
  Marker,
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import { useMapEvents } from "react-leaflet/hooks";
import { geojson, tileOSM } from "../../util/geo-util";
import { api } from "../../lib";
import { Modal, Spin, Image, Select, Row, Col, Space, Button } from "antd";
import { CheckOutlined } from "@ant-design/icons";
import { Chart } from "../supports";
import { CloseCircleOutlined } from "@ant-design/icons";
import { generateAdvanceFilterURL } from "../../util/utils";
import { UIState } from "../../state/ui";
import isEmpty from "lodash/isEmpty";
import sortBy from "lodash/sortBy";

const defZoom = 7;
const defCenter = window.mapConfig.center;

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
          click: () => {
            getChartData(id);
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
  iconUrl: require("../../location.svg").default,
  iconSize: new L.Point(40, 47),
});

const createClusterCustomIcon = function (cluster) {
  return L.divIcon({
    html: `<span>${cluster.getChildCount()}</span>`,
    className: "custom-marker-cluster",
    iconSize: L.point(50, 50, true),
  });
};

const Map = () => {
  // use tile layer from config
  const charts = window.charts;
  const showHistory = window.chart_features.show_history;
  const { advanceSearchValue } = UIState.useState((s) => s);
  const baseMap = tileOSM;
  const map = useRef();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [activePanel, setActivePanel] = useState(1);
  const [indicatorQuestion, setIndicatorQuestion] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState([]);

  const getIndicatorData = useCallback(() => {
    const url = `/question?attribute=indicator`;
    api
      .get(url)
      .then((res) => {
        setIndicatorQuestion(res?.data);
      })
      .catch((e) => console.error(e));
  }, []);

  useEffect(() => {
    setLoading(true);
    let url = `data/maps`;
    url = generateAdvanceFilterURL(advanceSearchValue, url);
    api
      .get(url)
      .then((res) => {
        setData(res.data);
        getIndicatorData();
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [advanceSearchValue, getIndicatorData]);

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

  // Indicator filter functions
  const handleOnChangeQuestionDropdown = (id) => {
    const filterQuestion = indicatorQuestion.find((q) => q.id === id);
    setSelectedQuestion(filterQuestion);
  };

  const handleOnChangeQuestionOption = (value, type) => {
    console.info(value, type);
  };

  return (
    <>
      <div id="map-view">
        <div className="map-container">
          <IndicatorDropDown
            indicatorQuestion={indicatorQuestion}
            handleOnChangeQuestionDropdown={handleOnChangeQuestionDropdown}
            selectedQuestion={selectedQuestion}
            handleOnChangeQuestionOption={handleOnChangeQuestionOption}
          />
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
            <MarkerClusterGroup iconCreateFunction={createClusterCustomIcon}>
              {!loading && (
                <Markers
                  zoom={defZoom}
                  data={data}
                  getChartData={getChartData}
                />
              )}
            </MarkerClusterGroup>
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
              <RegistrationDetail data={chartData} />
              <Chart
                activePanel={activePanel}
                setActivePanel={setActivePanel}
                chartData={chartData}
                getChartDataWithHistory={getChartDataWithHistory}
              />
            </>
          )}
        </Modal>
      </div>
    </>
  );
};

const IndicatorDropDown = ({
  indicatorQuestion,
  handleOnChangeQuestionDropdown,
  selectedQuestion,
  handleOnChangeQuestionOption,
}) => {
  return (
    <div className="indicator-dropdown-container">
      <Row>
        <Col span={24}>
          <Select
            dropdownMatchSelectWidth={false}
            placement={"bottomLeft"}
            showSearch
            placeholder="Select indicator"
            optionFilterProp="children"
            filterOption={(input, option) =>
              (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
            }
            options={indicatorQuestion.map((q) => ({
              label: q.name,
              value: q.id,
            }))}
            onChange={(val) => handleOnChangeQuestionDropdown(val)}
          />
          {!isEmpty(selectedQuestion) && (
            <div className="options-container">
              <RenderQuestionOption
                selectedQuestion={selectedQuestion}
                handleOnChangeQuestionOption={handleOnChangeQuestionOption}
              />
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
};

const RenderQuestionOption = ({
  selectedQuestion,
  handleOnChangeQuestionOption,
}) => {
  const MultipleOptionToRender = ({ option }) => {
    return sortBy(option, "order").map((opt) => (
      <Button
        key={`${opt.id}-${opt.name}`}
        type="primary"
        icon={<CheckOutlined />}
        onClick={(e) => handleOnChangeQuestionOption(e, selectedQuestion?.type)}
      >
        {opt.name}
      </Button>
    ));
  };

  if (selectedQuestion?.type === "option") {
    return (
      <Space direction="vertical">
        <MultipleOptionToRender
          option={selectedQuestion.option}
          questionId={selectedQuestion.id}
        />
      </Space>
    );
  }

  return <div>tes</div>;
};

const RegistrationDetail = ({ data }) => {
  const { registration } = data;
  if (!registration && !registration?.length) {
    return "";
  }
  return (
    <div className="registration-table">
      {registration?.map((detail) => {
        let answerValue = (
          <div className="registration-answer">{detail.value}</div>
        );
        if (detail.type === "photo") {
          answerValue = (
            <div className="registration-answer">
              <Image src={detail.value} />
            </div>
          );
        }
        return (
          <div className="registration-row" key={detail.question_id}>
            <div className="registration-question">{detail.question}:</div>
            {answerValue}
          </div>
        );
      })}
    </div>
  );
};

export default Map;
