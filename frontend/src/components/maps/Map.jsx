/* eslint-disable react-hooks/exhaustive-deps */
import React, {
  useEffect,
  useState,
  useRef,
  useMemo,
  useCallback,
} from "react";
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
import { api, ds } from "../../lib";
import { generateAdvanceFilterURL, generateFilterURL } from "../../util/utils";
import { UIState } from "../../state/ui";
import IndicatorDropdown from "./IndicatorDropdown";
import SchoolDetailModal from "./SchoolDetailModal";
import { Chart } from "..";
import { Card, Spin, Button, Space } from "antd";
import Draggable from "react-draggable";
import { isEmpty, intersection, uniqBy } from "lodash";
import { LoadingOutlined } from "@ant-design/icons";

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

  const [initMapPagination, setInitMapPagination] = useState({});
  const [initMapData, setInitMapData] = useState([]);

  useEffect(() => {
    const findQ = indicatorQuestions.find(
      (q) => q.id === mapFilterConfig?.defaultIndicator
    );
    if (findQ) {
      setSelectedQuestion(findQ);
    }
  }, [indicatorQuestions]);

  // ** Init maps data
  useEffect(() => {
    setLoading(true);
    const { page, perPage } = defPagination;
    const url = `/data/maps-init?page_only=true&page=${page}&perpage=${perPage}`;
    // ** fetch data from indexed DB first
    ds.getMap(url).then((cachedData) => {
      if (!cachedData) {
        api
          .get(url)
          .then((res) => {
            const { current, total_page } = res.data;
            ds.saveMap({ endpoint: url, data: res.data });
            setInitMapPagination({
              ...defPagination,
              page: current,
              totalPage: total_page,
            });
          })
          .catch((e) => {
            console.error("Unable to fetch page size", e);
          });
      } else {
        const { current, total_page } = cachedData.data;
        setInitMapPagination({
          ...defPagination,
          page: current,
          totalPage: total_page,
        });
      }
    });
  }, []);

  // ** Init maps data
  const fetchInitMapData = useCallback(async () => {
    if (isEmpty(initMapPagination)) {
      return;
    }
    const { page, totalPage, perPage } = initMapPagination;
    const url = "/data/maps-init";
    let curr = page;
    while (curr <= totalPage) {
      // pagination
      const pageURL = `${url}?page=${curr}&perpage=${perPage}`;
      // ** fetch data from indexed DB first
      await ds.getMap(pageURL).then(async (cachedData) => {
        if (!cachedData) {
          const res = await api.get(pageURL);
          const dataTemp = res?.data?.data || [];
          ds.saveMap({ endpoint: pageURL, data: dataTemp });
          setInitMapData((prevData) =>
            uniqBy([...prevData, ...dataTemp], "id")
          );
        } else {
          const dataTemp = cachedData?.data || [];
          setTimeout(() => {
            setInitMapData((prevData) =>
              uniqBy([...prevData, ...dataTemp], "id")
            );
          }, 100);
        }
      });
      curr += 1;
    }
  }, [initMapPagination]);

  // ** Init maps data
  useEffect(() => {
    fetchInitMapData();
  }, [fetchInitMapData]);

  // ** Filtered data
  const endpointURL = useMemo(() => {
    if (isEmpty(selectedQuestion)) {
      return null;
    }
    setData([]);
    setPagination(defPagination);
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

  // ** Filtered data
  useEffect(() => {
    if (endpointURL) {
      // get page size
      setLoading(true);
      const { page, perPage } = defPagination;
      const queryUrlPrefix = endpointURL.includes("?") ? "&" : "?";
      const url = `${endpointURL}${queryUrlPrefix}page_only=true&page=${page}&perpage=${perPage}`;
      // ** fetch data from indexed DB first
      ds.getMap(url).then((cachedData) => {
        if (!cachedData) {
          api
            .get(url)
            .then((res) => {
              const { current, total_page } = res.data;
              ds.saveMap({ endpoint: url, data: res.data });
              setPagination({
                ...defPagination,
                page: current,
                totalPage: total_page,
              });
            })
            .catch((e) => {
              console.error("Unable to fetch page size", e);
            });
        } else {
          const { current, total_page } = cachedData.data;
          setPagination({
            ...defPagination,
            page: current,
            totalPage: total_page,
          });
        }
      });
    }
  }, [defPagination, endpointURL]);

  // ** Filtered data
  const fetchData = useCallback(async () => {
    if (isEmpty(pagination) || !endpointURL) {
      return;
    }
    const { page, totalPage, perPage } = pagination;
    let curr = page;
    while (curr <= totalPage) {
      // pagination
      const queryUrlPrefix = endpointURL.includes("?") ? "&" : "?";
      const pageURL = `${endpointURL}${queryUrlPrefix}page=${curr}&perpage=${perPage}`;
      // ** fetch data from indexed DB first
      await ds.getMap(pageURL).then(async (cachedData) => {
        if (!cachedData) {
          const res = await api.get(pageURL);
          const dataTemp = res?.data?.data || [];
          ds.saveMap({ endpoint: pageURL, data: dataTemp });
          setData((prevData) => uniqBy([...prevData, ...dataTemp], "id"));
        } else {
          const dataTemp = cachedData?.data || [];
          setTimeout(() => {
            setData((prevData) => uniqBy([...prevData, ...dataTemp], "id"));
          }, 100);
        }
      });
      curr += 1;
    }
  }, [pagination, endpointURL]);

  // ** Filtered data
  useEffect(() => {
    fetchData().finally(() => {
      setLoading(false);
    });
  }, [fetchData]);

  // ** Filtered data
  const filteredData = useMemo(() => {
    if (isEmpty(data)) {
      return [];
    }
    let remapDataWithInitData = data.map((d) => {
      const findInitData = initMapData.find((imd) => imd.id === d.id);
      return {
        ...d,
        ...findInitData,
      };
    });
    remapDataWithInitData = uniqBy(remapDataWithInitData, "id");
    const { type, option } = selectedQuestion;
    if (type === "number") {
      const { minNumber, maxNumber } = barChartValues;
      if (!maxNumber && minNumber === maxNumber) {
        // do not filter when first load
        return remapDataWithInitData;
      }
      return remapDataWithInitData.filter((d) => {
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
      return remapDataWithInitData.filter(
        (d) => !selectedOption.includes(d.answer)
      );
    }
    return remapDataWithInitData;
  }, [selectedQuestion, selectedOption, barChartValues, data, initMapData]);

  useEffect(() => {
    UIState.update((s) => {
      s.mapData = filteredData.map((d) => {
        if (!d?.school_information) {
          return d;
        }
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
          obj[item.answer] = obj[item.answer] || {
            name: item.answer,
            color: selectedQuestion?.option?.find((f) => f.name === item.answer)
              ?.color,
            count: 0,
          };
          obj[item.answer].count++;
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
      // minNumber: val.startValue,
      // maxNumber: val.endValue,
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
                    // loading={loading}
                    disableEvent={loading}
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
              <Markers
                zoom={defZoom}
                selectedQuestion={selectedQuestion}
                searchValue={searchValue}
                mapData={mapData}
                setSelectedDatapoint={setSelectedDatapoint}
              />
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
    .map((d, di) => {
      const { id, geo, answer, school_information, year_conducted } = d;
      const isHovered = id === hovered;
      return (
        <Marker
          key={`marker-${id}-${di}`}
          position={geo}
          answerValue={answer}
          selectedQuestion={selectedQuestion}
          icon={
            new L.divIcon({
              className: "custom-marker",
              iconSize: [32, 32],
              html: `<span style="background-color:${
                selectedQuestion?.option?.find((f) => f.name === answer)
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
        value: item?.options?.answerValue,
        color: item?.options?.selectedQuestion?.option?.find(
          (f) => f.name === item?.options?.answerValue
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
