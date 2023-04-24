/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState, useRef } from "react";
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
import { generateAdvanceFilterURL } from "../../util/utils";
import { UIState } from "../../state/ui";
import IndicatorDropdown from "./IndicatorDropdown";
import { Chart } from "../";
import { Card } from "antd";
import Draggable from "react-draggable";

const defZoom = 7;
const defCenter = window.mapConfig.center;

const Map = ({ selectedProvince, selectedSchoolType }) => {
  // use tile layer from config
  const {
    advanceSearchValue,
    provinceValues,
    schoolTypeValues,
    indicatorQuestions,
  } = UIState.useState((s) => s);
  const baseMap = tileOSM;
  const map = useRef();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  // const [activePanel, setActivePanel] = useState(1);
  const [selectedQuestion, setSelectedQuestion] = useState({});
  const [selectedOption, setSelectedOption] = useState([]);
  const [roseChartValues, setRoseChartValues] = useState([]);
  const [barChartValues, setBarChartValues] = useState({
    startValue: 0,
    endValue: 100,
  });

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
        UIState.update((s) => {
          s.mapData = res.data;
        });
      })
      .catch((e) => console.error(e))
      .finally(() => setLoading(false));
  }, [
    advanceSearchValue,
    selectedQuestion,
    selectedProvince,
    selectedSchoolType,
  ]);

  useEffect(() => {
    if (data.length > 0 && selectedQuestion.type === "option") {
      const results = Object.values(
        data.reduce((obj, item) => {
          obj[item.answer.value] = obj[item.answer.value] || {
            name: item.answer.value,
            color: selectedQuestion?.option?.find(
              (f) => f.name === item.answer.value
            )?.color,
            count: 0,
          };
          obj[item.answer.value].count++;
          return obj;
        }, {})
      );
      setRoseChartValues(results);
    }
  }, [data]);

  // Indicator filter functions
  const handleOnChangeQuestionDropdown = (id) => {
    const filterQuestion = indicatorQuestions.find((q) => q.id === id);
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

  return (
    <>
      <div id="map-view">
        <div className="map-container">
          <IndicatorDropdown
            indicatorQuestion={indicatorQuestions}
            handleOnChangeQuestionDropdown={handleOnChangeQuestionDropdown}
            selectedQuestion={selectedQuestion}
            handleOnChangeQuestionOption={handleOnChangeQuestionOption}
            selectedOption={selectedOption}
            setValues={setValuesOfNumber}
            barChartValues={barChartValues}
          />
          {selectedQuestion.type === "option" && (
            <Draggable>
              <div className="map-chart-container">
                <Card>
                  <Chart
                    height={350}
                    excelFile={"title"}
                    type={"PIE"}
                    data={roseChartValues.map((v) => ({
                      name: v.name,
                      value: v.count,
                      count: v.count,
                      color: v.color,
                    }))}
                    wrapper={false}
                    horizontal={false}
                  />
                </Card>
              </div>
            </Draggable>
          )}
          <MapContainer
            ref={map}
            center={defCenter}
            zoom={defZoom}
            scrollWheelZoom={false}
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
                  selectedQuestion={selectedQuestion}
                />
              )}
            </MarkerClusterGroup>
          </MapContainer>
        </div>
      </div>
    </>
  );
};

const Markers = ({ zoom, data, selectedQuestion }) => {
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
        selectedQuestion={selectedQuestion}
        icon={
          new L.divIcon({
            className: "custom-marker",
            iconSize: [32, 32],
            html: `<span style="background-color:${
              selectedQuestion?.option?.find((f) => f.name === answer?.value)
                ?.color || "#2EA745"
            }"/>`,
          })
        }
        eventHandlers={{
          mouseover: () => setHovered(id),
          mouseout: () => setHovered(null),
        }}
      >
        <Tooltip direction="top">{name}</Tooltip>
      </Marker>
    );
  });
};

const createClusterCustomIcon = (cluster) => {
  const color = ["#4475B4", "#73ADD1", "#AAD9E8", "#70CFAD"];

  const tempResult = {};

  cluster
    .getAllChildMarkers()
    .map((item) => {
      return {
        ...item?.options?.answerValue,
        color: item?.options?.selectedQuestion?.option?.find(
          (f) => f.name === item?.options?.answerValue?.value
        )?.color,
      };
    })
    .map((element, index) => {
      tempResult[element.value] = {
        value: element.value,
        question: element.question,
        color: element?.color || color[index],
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
    html: `<svg width="100%" height="100%" viewBox="0 0 100 100"> <circle cx="50" cy="50" r="40" fill="#ffffffad"/>
          ${result
            .map((item, index) => {
              const v = index === 0 ? circleLength : spaceLeft;
              spaceLeft -= (item.count / totalValue) * circleLength;
              return `
                <circle cx="50" cy="50" r="40" fill="transparent" stroke-width="15" stroke="${
                  item.color ? item.color : color[index]
                }" stroke-dasharray="${v} ${circleLength}" />`;
            })
            .join(
              ""
            )} <text x="50" y="50" fill="black" font-size="14">${cluster.getChildCount()}</text></svg>`,
    className: `custom-marker-cluster`,
    iconSize: L.point(60, 60, true),
  });
};

export default Map;
