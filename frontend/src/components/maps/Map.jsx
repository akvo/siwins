/* eslint-disable react-hooks/exhaustive-deps */
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
import {
  Modal,
  Spin,
  Image,
  Select,
  Row,
  Col,
  Space,
  Button,
  Card,
  Collapse,
} from "antd";
import { CloseCircleFilled, CheckCircleFilled } from "@ant-design/icons";
import { generateAdvanceFilterURL } from "../../util/utils";
import { UIState } from "../../state/ui";
import isEmpty from "lodash/isEmpty";
import sortBy from "lodash/sortBy";
import { Chart } from "../";

const { Panel } = Collapse;

const defZoom = 7;
const defCenter = window.mapConfig.center;

const Markers = ({ zoom, data, getChartData }) => {
  const [hovered, setHovered] = useState(null);
  const [currentZoom, setCurrentZoom] = useState(zoom);

  const map = useMapEvents({
    zoomend: () => setCurrentZoom(map?._zoom || currentZoom),
  });

  data = data.filter((d) => d.geo);
  return data.map(({ id, geo, name, answer }) => {
    const isHovered = id === hovered;
    console.info(isHovered);
    return (
      <Marker
        key={id}
        position={geo}
        answerValue={answer}
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

const createClusterCustomIcon = (cluster) => {
  const color = ["#4475B4", "#73ADD1", "#AAD9E8", "#70CFAD"];

  const tempResult = {};

  cluster
    .getAllChildMarkers()
    .map((item) => item?.options?.answerValue)
    .map((element, index) => {
      tempResult[element.value] = {
        value: element.value,
        question: element.question,
        color: color[index],
        count: tempResult[element.value]
          ? tempResult[element.value].count + 1
          : 1,
      };
    });
  const result = Object.values(tempResult);

  const totalValue = result.reduce((s, { count }) => s + count, 0);
  const radius = 40;
  const circleLength = Math.PI * (radius * 2);
  let spaceLeft = circleLength;

  return L.divIcon({
    html: `<svg width="100%" height="100%" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="#ffffffad"/>
    ${result
      .map((item, index) => {
        const v = index === 0 ? circleLength : spaceLeft;
        spaceLeft -= (item.count / totalValue) * circleLength;
        return `
          <circle cx="50" cy="50" r="40" fill="transparent" stroke-width="15" stroke="${color[index]}" stroke-dasharray="${v} ${circleLength}" />`;
      })
      .join(
        ""
      )}   <text x="50" y="50" fill="black" font-size="14">${cluster.getChildCount()}</text></svg>`,
    className: `custom-marker-cluster`,
    iconSize: L.point(60, 60, true),
  });
};

const Map = () => {
  // use tile layer from config
  const charts = window.charts;
  const showHistory = window.chart_features.show_history;
  const { advanceSearchValue, provinceValues, schoolTypeValues } =
    UIState.useState((s) => s);
  const baseMap = tileOSM;
  const map = useRef();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [selectedPoint, setSelectedPoint] = useState(null);
  const [chartData, setChartData] = useState(null);
  // const [activePanel, setActivePanel] = useState(1);
  const [indicatorQuestion, setIndicatorQuestion] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState({});
  const [selectedOption, setSelectedOption] = useState([]);
  const [selectedProvince, setSelectedProvince] = useState([]);
  const [selectedSchoolType, setSelectedSchoolType] = useState([]);
  const [barChartValues, setBarChartValues] = useState({
    startValue: 0,
    endValue: 100,
  });

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
    if (indicatorQuestion.length === 0) {
      getIndicatorData();
    }
  }, [getIndicatorData, indicatorQuestion]);

  useEffect(() => {
    Promise.all([
      api.get("/cascade/school_information?level=province"),
      api.get("/cascade/school_information?level=school_type"),
    ]).then((res) => {
      const [province, school_type] = res;
      UIState.update((s) => {
        s.provinceValues = province?.data;
        s.schoolTypeValues = school_type?.data;
      });
    });
  }, []);

  console.log(provinceValues);

  useEffect(() => {
    setLoading(true);
    let url = `data/maps`;
    url = generateAdvanceFilterURL(advanceSearchValue, url);
    const urlParams = new URLSearchParams(url);
    if (selectedQuestion?.id && !urlParams.get("indicator")) {
      url = `${url}?indicator=${selectedQuestion?.id}`;
    }
    if (selectedProvince && selectedProvince.length > 0) {
      const queryUrlPrefix = url.includes("?") ? "&" : "?";
      url = `${url}${queryUrlPrefix}prov=${provinceValues
        .filter((item) => !selectedProvince?.includes(item.name))
        .map((x) => x.name)
        .join("&prov=")}`;
    }
    if (selectedSchoolType && selectedSchoolType.length > 0) {
      const queryUrlPrefix = url.includes("?") ? "&" : "?";
      url = `${url}${queryUrlPrefix}sctype=${schoolTypeValues
        .filter((item) => !selectedSchoolType?.includes(item.name))
        .map((x) => x.name)
        .join("&sctype=")}`;
    }
    api
      .get(url)
      .then((res) => {
        setData(res.data);
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [
    advanceSearchValue,
    selectedQuestion,
    selectedProvince,
    selectedSchoolType,
  ]);

  console.log(selectedProvince);

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

  // const getChartDataWithHistory = (id, question_id) => {
  //   const url = `/data/chart/${id}?history=true&question_ids=${question_id}`;
  //   api
  //     .get(url)
  //     .then((res) => {
  //       const currentData = chartData;
  //       const currentMonitoring = currentData.monitoring.filter(
  //         (m) => m.question_id !== question_id
  //       );
  //       const newMonitoring = res.data.monitoring.map((m) => ({
  //         show_history: true,
  //         ...m,
  //       }));
  //       setChartData({
  //         ...currentData,
  //         monitoring: [...currentMonitoring, ...newMonitoring],
  //       });
  //     })
  //     .catch((e) => console.error(e));
  // };

  // Indicator filter functions
  const handleOnChangeQuestionDropdown = (id) => {
    const filterQuestion = indicatorQuestion.find((q) => q.id === id);
    setSelectedQuestion(filterQuestion);
    updateGlobalState([], "option");
  };

  const handleOnChangeQuestionOption = (value) => {
    let newArray = [];
    if (selectedOption.includes(value)) {
      newArray = selectedOption.filter((e) => e !== value);
      setSelectedOption(newArray);
    } else {
      newArray = [...selectedOption, value];
      setSelectedOption(newArray);
    }
    filterIndicatorOption(newArray);
  };

  const updateGlobalState = (value, type) => {
    const filterAdvanceSearchValue = advanceSearchValue.filter(
      (x) => x.qid !== selectedQuestion?.id
    );
    let updatedValue = [
      {
        qid: selectedQuestion?.id,
        question: selectedQuestion?.name,
        ...(type === "number" ? { number: value } : { option: value }),
        type: type,
        filter: "indicator",
      },
    ];
    if (Array.isArray(value)) {
      updatedValue = value.length ? updatedValue : [];
    }
    UIState.update((s) => {
      s.advanceSearchValue = [...filterAdvanceSearchValue, ...updatedValue];
    });
  };

  const filterIndicatorOption = (array) => {
    const value = selectedQuestion?.option
      .filter((item) => !array?.includes(item.name))
      .map((filterValue) => `${selectedQuestion.id}|${filterValue.name}`);
    updateGlobalState(value, "option");
  };

  const setValuesOfNumber = (val) => {
    const value = [
      selectedQuestion.number[val.startValue]?.value,
      selectedQuestion.number[val.endValue]?.value,
    ];
    setBarChartValues({
      startValue: val.start,
      endValue: val.end,
    });
    updateGlobalState(value, "number");
  };

  const handleProvinceFilter = (value) => {
    if (selectedProvince.includes(value)) {
      setSelectedProvince(selectedProvince.filter((e) => e !== value));
    } else {
      setSelectedProvince([...selectedProvince, value]);
    }
  };

  const handleSchoolTypeFilter = (value) => {
    if (selectedSchoolType.includes(value)) {
      setSelectedSchoolType(selectedSchoolType.filter((e) => e !== value));
    } else {
      setSelectedSchoolType([...selectedSchoolType, value]);
    }
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
            selectedOption={selectedOption}
            setValues={setValuesOfNumber}
            barChartValues={barChartValues}
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
          <BottomFilter
            provinceValues={provinceValues}
            schoolTypeValues={schoolTypeValues}
            handleSchoolTypeFilter={handleSchoolTypeFilter}
            handleProvinceFilter={handleProvinceFilter}
            selectedProvince={selectedProvince}
            selectedSchoolType={selectedSchoolType}
          />
        </div>

        {/* Chart Modal */}
        <Modal
          title={
            <>
              <div className="title-holder">
                <p>{selectedPoint?.name}</p>
                <CloseCircleFilled
                  onClick={() => {
                    setSelectedPoint(null);
                    // setActivePanel(1);
                  }}
                />
              </div>
            </>
          }
          open={selectedPoint}
          onCancel={() => {
            setSelectedPoint(null);
            // setActivePanel(1);
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
            </>
          )}
        </Modal>
      </div>
    </>
  );
};

const BottomFilter = ({
  provinceValues,
  schoolTypeValues,
  handleProvinceFilter,
  handleSchoolTypeFilter,
  selectedProvince,
  selectedSchoolType,
}) => {
  return (
    <div className="bottom-filter-container">
      <Collapse>
        <Panel header="SCHOOL TYPE" key="1">
          <Space direction="vertical" size="small" style={{ display: "flex" }}>
            {schoolTypeValues?.map((item) => (
              <Button
                key={`${item.name}`}
                type="link"
                icon={
                  selectedSchoolType.includes(item.name) ? (
                    <CloseCircleFilled />
                  ) : (
                    <CheckCircleFilled />
                  )
                }
                className={`${
                  selectedSchoolType.includes(item.name) ? "selected" : ""
                }`}
                onClick={() => handleSchoolTypeFilter(item.name)}
              >
                {item.name}
              </Button>
            ))}
            <Button
              type="primary"
              onClick={() => console.info("item.name")}
              className="enable-button"
            >
              Enable All
            </Button>
          </Space>
        </Panel>
        <Panel header="PROVINCE" key="2">
          <Space direction="vertical" size="small" style={{ display: "flex" }}>
            {provinceValues?.map((item) => (
              <Button
                key={`${item.name}`}
                type="link"
                onClick={() => handleProvinceFilter(item.name)}
                icon={
                  selectedProvince.includes(item.name) ? (
                    <CloseCircleFilled />
                  ) : (
                    <CheckCircleFilled />
                  )
                }
                className={`${
                  selectedProvince.includes(item.name) ? "selected" : ""
                }`}
              >
                {item.name}
              </Button>
            ))}
            <Button
              type="primary"
              onClick={() => console.info("item.name")}
              className="enable-button"
            >
              Enable All
            </Button>
          </Space>
        </Panel>
      </Collapse>
    </div>
  );
};

const IndicatorDropDown = ({
  indicatorQuestion,
  handleOnChangeQuestionDropdown,
  selectedQuestion,
  handleOnChangeQuestionOption,
  selectedOption,
  setValues,
  barChartValues,
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
                selectedOption={selectedOption}
                setValues={setValues}
                barChartValues={barChartValues}
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
  selectedOption,
  setValues,
  barChartValues,
}) => {
  const MultipleOptionToRender = ({ option }) => {
    return sortBy(option, "order").map((opt) => (
      <Button
        style={{
          backgroundColor: selectedOption.includes(opt.name)
            ? "#222"
            : "#1677ff",
        }}
        key={`${opt.id}-${opt.name}`}
        type="primary"
        icon={
          selectedOption.includes(opt.name) ? (
            <CloseCircleFilled />
          ) : (
            <CheckCircleFilled />
          )
        }
        onClick={() =>
          handleOnChangeQuestionOption(opt.name, selectedQuestion?.type)
        }
      >
        {opt.name}
      </Button>
    ));
  };

  const NumberOptionToRender = ({ option }) => {
    return (
      <Row>
        <Col className="chart-card" span={24}>
          <Card>
            <Chart
              height={350}
              excelFile={"title"}
              type={"BAR"}
              data={option.map((v) => ({
                name: v.value,
                value: v.count,
                count: v.count,
                color: "#70CFAD",
              }))}
              wrapper={false}
              horizontal={false}
              loading={false}
              dataZoom={[
                {
                  type: "inside",
                  realtime: false,
                  start: barChartValues.startValue,
                  end: barChartValues.endValue,
                },
                {
                  type: "slider",
                  realtime: false,
                  start: barChartValues.startValue,
                  end: barChartValues.endValue,
                },
              ]}
              grid={{
                top: 80,
                bottom: 80,
                left: 40,
                right: 20,
                show: true,
                containLabel: true,
                label: {
                  color: "#222",
                },
              }}
              setValues={setValues}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  if (selectedQuestion.type === "number") {
    return <NumberOptionToRender option={selectedQuestion.number} />;
  }

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
