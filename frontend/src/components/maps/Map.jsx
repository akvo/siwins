/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState, useRef, useMemo } from "react";
import "./style.scss";
import "leaflet/dist/leaflet.css";
import {
  MapContainer,
  GeoJSON,
  TileLayer,
  Popup,
  Marker,
  useMap,
} from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import L from "leaflet";
import { useMapEvents } from "react-leaflet/hooks";
import { geojson, tileOSM } from "../../util/geo-util";
import { api } from "../../lib";
import { generateAdvanceFilterURL, generateFilterURL } from "../../util/utils";
import { UIState } from "../../state/ui";
import IndicatorDropdown from "./IndicatorDropdown";
import SchoolDetailModal from "./SchoolDetailModal";
import { Chart } from "..";
import { Card, Spin, Button, Space } from "antd";
import Draggable from "react-draggable";
import { isEmpty, intersection } from "lodash";
import { LoadingOutlined } from "@ant-design/icons";
import { sequentialPromise } from "../../util/utils";

const defZoom = 7;
const defCenter = window.mapConfig.center;
const defPagination = {
  page: 1,
  perPage: 100,
  totalPage: 0,
};
const mapFilterConfig = window.mapFilterConfig;
const barChartDefValues = {
  startValue: 0,
  endValue: 0,
  minNumber: 0,
  maxNumber: 0,
};

const Map = ({ searchValue }) => {
  // use tile layer from config
  const {
    advanceSearchValue,
    indicatorQuestions,
    mapData,
    provinceFilterValue,
  } = UIState.useState((s) => s);
  const baseMap = tileOSM;
  const map = useRef();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [selectedRoseChartValue, setSelectedRoseChartValue] = useState("");
  const [selectedQuestion, setSelectedQuestion] = useState({});
  const [selectedOption, setSelectedOption] = useState([]);
  const [barChartValues, setBarChartValues] = useState(barChartDefValues);
  const [selectedDatapoint, setSelectedDatapoint] = useState({});
  const [pagination, setPagination] = useState({});

  useEffect(() => {
    const findQ = indicatorQuestions.find(
      (q) => q.id === mapFilterConfig?.defaultIndicator
    );
    if (findQ) {
      setSelectedQuestion(findQ);
    }
  }, [indicatorQuestions]);

  const endpointURL = useMemo(() => {
    if (isEmpty(selectedQuestion)) {
      return null;
    }
    let url = `data/maps`;
    url = generateAdvanceFilterURL(advanceSearchValue, url);
    const urlParams = new URLSearchParams(url);
    if (selectedQuestion?.id && !urlParams.get("indicator")) {
      const queryUrlPrefix = url.includes("?") ? "&" : "?";
      url = `${url}${queryUrlPrefix}indicator=${selectedQuestion?.id}`;
    }
    url = generateFilterURL(provinceFilterValue, url);
    return url;
  }, [advanceSearchValue, selectedQuestion, provinceFilterValue]);

  useEffect(() => {
    if (endpointURL) {
      // get page size
      setLoading(true);
      const { page, perPage } = defPagination;
      const queryUrlPrefix = endpointURL.includes("?") ? "&" : "?";
      api
        .get(
          `${endpointURL}${queryUrlPrefix}page_only=true&page=${page}&perpage=${perPage}`
        )
        .then((res) => {
          const { current, total_page } = res.data;
          setPagination({
            ...defPagination,
            page: current,
            totalPage: total_page,
          });
        })
        .catch((e) => {
          console.error("Unable to fetch page size", e);
        });
    }
  }, [defPagination, endpointURL]);

  const apiCalls = useMemo(() => {
    if (isEmpty(pagination) || !endpointURL) {
      return [];
    }
    const tempURL = [];
    const { page, totalPage, perPage } = pagination;
    let curr = page;
    while (curr <= totalPage) {
      // pagination
      const queryUrlPrefix = endpointURL.includes("?") ? "&" : "?";
      const pageURL = `${endpointURL}${queryUrlPrefix}page=${curr}&perpage=${perPage}`;
      tempURL.push(api.get(pageURL));
      curr += 1;
    }
    return tempURL;
  }, [pagination]);

  useEffect(() => {
    if (!isEmpty(apiCalls)) {
      sequentialPromise(apiCalls)
        .then((res) => {
          const paginatedData = res.map((item) => item.data).flat();
          const dataTemp = paginatedData.map((pd) => pd.data).flat();
          setData(dataTemp);
        })
        .finally(() => {
          setTimeout(() => {
            setLoading(false);
          }, 1000);
        });
    }
  }, [apiCalls]);

  const filteredData = useMemo(() => {
    if (isEmpty(data)) {
      return [];
    }
    const { type, option } = selectedQuestion;
    if (type === "number") {
      const { minNumber, maxNumber } = barChartValues;
      return data.filter((d) => {
        const { value } = d.answer;
        if (value >= minNumber && value <= maxNumber) {
          return d;
        }
      });
    }
    if (["jmp", "option"].includes(type)) {
      const optionNames = option.map((o) => o.name);
      const allOptionSelected =
        intersection(optionNames, selectedOption).length === option.length;
      if (allOptionSelected) {
        return [];
      }
      return data.filter((d) => !selectedOption.includes(d.answer.value));
    }
    return data;
  }, [selectedQuestion, selectedOption, data, barChartValues]);

  useEffect(() => {
    UIState.update((s) => {
      s.mapData = filteredData.map((d) => {
        const school_information_array = Object.values(d.school_information);
        return {
          ...d,
          school_information_array: school_information_array,
        };
      });
    });
  }, [filteredData]);

  const roseChartValues = useMemo(() => {
    if (["option", "jmp"].includes(selectedQuestion.type)) {
      let results = Object.values(
        mapData.reduce((obj, item) => {
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
      results = selectedQuestion?.option?.map((item) => {
        return {
          name: item.name,
          color: item.color,
          count: results.find((v) => v.name === item.name)?.count || 0,
        };
      });
      return results;
    }
    return [];
  }, [mapData]);

  // Indicator filter functions
  const handleOnChangeQuestionDropdown = (id) => {
    setSelectedOption([]);
    updateGlobalState([], "option");
    updateGlobalState([], "number");
    const filterQuestion = indicatorQuestions.find((q) => q.id === id);
    if (filterQuestion?.type === "number") {
      const numbers = filterQuestion?.number?.map((x) => x.value);
      setBarChartValues({
        ...barChartDefValues,
        endValue: numbers?.length ? numbers.length - 1 : 0,
      });
    }
    setSelectedQuestion(filterQuestion);
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
    // filterIndicatorOption(newArray);
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

  // # disable update global state and network call
  // const filterIndicatorOption = (array) => {
  //   const value = selectedQuestion?.option
  //     .filter((item) => !array?.includes(item.name))
  //     .map((filterValue) => `${selectedQuestion.id}|${filterValue.name}`);
  //   updateGlobalState(value, "option");
  // };

  const setValuesOfNumber = (val) => {
    setBarChartValues({
      ...barChartValues,
      startValue: val.startValue,
      endValue: val.endValue,
      minNumber: selectedQuestion.number[val.startValue]?.value,
      maxNumber: selectedQuestion.number[val.endValue]?.value,
    });
    // # disable update global state and network call
    // const value = [
    //   selectedQuestion.number[val.startValue]?.value,
    //   selectedQuestion.number[val.endValue]?.value,
    // ];
    // updateGlobalState(value, "number");
  };

  const chartClick = (p) => {
    if (selectedRoseChartValue === p) {
      setSelectedRoseChartValue(p);
      setSelectedOption([]);
      // filterIndicatorOption([]);
      return;
    }
    setSelectedRoseChartValue(p);
    setSelectedOption(
      selectedQuestion?.option
        ?.filter((e) => e.name !== p)
        .map((item) => item.name)
    );
    // filterIndicatorOption(
    //   selectedQuestion?.option
    //     ?.filter((e) => e.name !== p)
    //     .map((item) => item.name)
    // );
  };

  return (
    <>
      <div id="map-view">
        {loading && (
          <div className="map-loading">
            <Spin
              indicator={
                <LoadingOutlined
                  style={{ fontSize: 30, color: "#ffffff", opacity: 0.6 }}
                  spin
                />
              }
            />
          </div>
        )}
        <div className="map-container">
          <IndicatorDropdown
            loading={loading}
            indicatorQuestion={indicatorQuestions}
            handleOnChangeQuestionDropdown={handleOnChangeQuestionDropdown}
            selectedQuestion={selectedQuestion}
            handleOnChangeQuestionOption={handleOnChangeQuestionOption}
            selectedOption={selectedOption}
            setValues={setValuesOfNumber}
            barChartValues={barChartValues}
          />
          {["option", "jmp"].includes(selectedQuestion.type) && (
            <Draggable>
              <div className="map-chart-container">
                <Card>
                  <Chart
                    title={selectedQuestion?.name}
                    height={350}
                    excelFile={"title"}
                    type={"PIE"}
                    data={roseChartValues.map((v) => ({
                      name: v.name,
                      value: v.count,
                      count: v.count,
                      color: v.color,
                    }))}
                    legend={true}
                    showRoseChart={true}
                    wrapper={false}
                    horizontal={false}
                    callbacks={{ onClick: chartClick }}
                    grid={{
                      top: 90,
                    }}
                    loading={loading}
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
                  selectedQuestion={selectedQuestion}
                  searchValue={searchValue}
                  mapData={mapData}
                  setSelectedDatapoint={setSelectedDatapoint}
                />
              )}
            </MarkerClusterGroup>
          </MapContainer>
        </div>
      </div>
      <SchoolDetailModal
        selectedDatapoint={selectedDatapoint}
        setSelectedDatapoint={setSelectedDatapoint}
      />
    </>
  );
};

const Markers = ({
  zoom,
  selectedQuestion,
  searchValue,
  mapData,
  setSelectedDatapoint,
}) => {
  const [hovered, setHovered] = useState(null);
  const [currentZoom, setCurrentZoom] = useState(zoom);

  const map = useMapEvents({
    zoomend: () => setCurrentZoom(map?._zoom || currentZoom),
  });

  const mapHook = useMap();

  useEffect(() => {
    const findCordinates = mapData.find((item) =>
      item.school_information_array.includes(searchValue)
    );
    if (findCordinates?.geo) {
      mapHook.setView(findCordinates?.geo, 14);
    } else {
      mapHook.setView(defCenter, 7);
    }
  }, [searchValue]);

  return mapData
    .filter((d) => d.geo)
    .map((d) => {
      const { id, geo, answer, school_information, year_conducted } = d;
      const isHovered = id === hovered;
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
              }; border:${isHovered ? "2px solid #fff" : ""};"/>`,
            })
          }
          eventHandlers={{
            mouseover: () => setHovered(id),
            mouseout: () => setHovered(null),
            // click: () => {
            //   mapHook.setView(geo, 14);
            // },
          }}
        >
          <Popup direction="top">
            <Space direction="vertical">
              <div>
                <div>
                  <b>School: </b>
                  {`${school_information?.["school_name"]} (${school_information?.["school_code"]})`}
                </div>
                <div>
                  <b>School Type: </b>
                  {`${school_information?.["school_type"]}`}
                </div>
                <div>
                  <b>Province: </b>
                  {`${school_information?.["province"]}`}
                </div>
                <div key={`popup-${id}-year_conducted`}>
                  <b>Last updated: </b>
                  {year_conducted}
                </div>
              </div>
              <Button
                type="primary"
                size="small"
                ghost
                block
                onClick={() => setSelectedDatapoint(d)}
              >
                View Details
              </Button>
            </Space>
          </Popup>
        </Marker>
      );
    });
};

const createClusterCustomIcon = (cluster) => {
  // const color = ["#4475B4", "#73ADD1", "#AAD9E8", "#70CFAD"];
  const color = ["#4475B4"];
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
            )} <text x="50%" y="50%" fill="black" text-anchor="middle" dy=".3em" font-size="18px">${cluster.getChildCount()}</text></svg>`,
    className: `custom-marker-cluster`,
    iconSize: L.point(60, 60, true),
  });
};

export default Map;
