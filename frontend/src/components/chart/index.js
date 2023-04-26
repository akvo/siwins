import React, { useEffect, useState, useCallback } from "react";
import { Col, Card } from "antd";
import ReactECharts from "echarts-for-react";
import { Bar, BarStack, Pie } from "./options";

export const generateOptions = (
  { type, data, chartTitle, excelFile },
  extra,
  series,
  legend,
  horizontal,
  highlighted,
  axis,
  grid,
  dataZoom
) => {
  switch (type) {
    case "BARSTACK":
      return BarStack(
        data,
        chartTitle,
        extra,
        excelFile,
        horizontal,
        highlighted
      );
    case "PIE":
      return Pie(data, chartTitle, extra, series);
    default:
      return Bar(
        data,
        chartTitle,
        excelFile,
        extra,
        legend,
        horizontal,
        grid,
        dataZoom,
        axis
      );
  }
};

const loadingStyle = {
  text: "Loading",
  color: "#1890ff",
  textColor: "rgba(0,0,0,.85)",
  maskColor: "rgba(255, 255, 255, 1)",
  zlevel: 0,
  fontSize: "1.17em",
  showSpinner: true,
  spinnerRadius: 10,
  lineWidth: 5,
  fontWeight: "500",
  fontStyle: "normal",
  fontFamily: "Poppins",
};

const Chart = ({
  type,
  title = "",
  subTitle = "",
  excelFile = "",
  height = 450,
  span = 12,
  data,
  extra = {},
  wrapper = true,
  axis = null,
  horizontal = false,
  styles = {},
  transform = true,
  series,
  legend,
  callbacks = null,
  highlighted,
  loading = false,
  loadingOption = loadingStyle,
  grid = {},
  cumulative = false,
  colorConfig = {},
  dataZoom = {},
  setValues,
}) => {
  const [echartsReactRef, setEchartsReactRef] = useState();
  if (transform) {
    data = data.map((x) => ({
      ...x,
      name: x.name,
      var: x.name,
    }));
  }
  const chartTitle = wrapper ? {} : { title: title, subTitle: subTitle };
  const option = generateOptions(
    {
      type: type,
      data: data,
      chartTitle: chartTitle,
      excelFile: excelFile,
      cumulative: cumulative,
      colorConfig: colorConfig,
    },
    extra,
    series,
    legend,
    horizontal,
    highlighted,
    axis,
    grid,
    dataZoom
  );
  const onEvents = {
    click: (e) => {
      if (callbacks?.onClick) {
        callbacks.onClick(e.data?.cbParam);
      }
    },
  };

  const dataZoomFunc = useCallback(() => {
    const echartsInstance = echartsReactRef.getEchartsInstance();
    const startValue = echartsInstance.getOption().dataZoom[0].startValue;
    const start = echartsInstance.getOption().dataZoom[0].start;
    const end = echartsInstance.getOption().dataZoom[0].end;
    const endValue = echartsInstance.getOption().dataZoom[0].endValue;
    setValues({
      startValue: startValue,
      endValue: endValue,
      start: start,
      end: end,
    });
  }, [echartsReactRef, setValues]);

  useEffect(() => {
    if (echartsReactRef) {
      const echartsInstance = echartsReactRef.getEchartsInstance();
      echartsInstance.on("dataZoom", dataZoomFunc);
    }
  }, [echartsReactRef, option, dataZoomFunc]);

  if (wrapper) {
    return (
      <Col
        sm={24}
        md={span * 2}
        lg={span}
        style={{ height: height, ...styles }}
      >
        <Card title={title}>
          <ReactECharts
            option={option}
            notMerge={true}
            style={{ height: height - 50, width: "100%" }}
            onEvents={onEvents}
            showLoading={loading}
            loadingOption={loadingOption}
            ref={(e) => setEchartsReactRef(e)}
          />
        </Card>
      </Col>
    );
  }
  return (
    <ReactECharts
      option={option}
      notMerge={true}
      style={{ height: height - 50, width: "100%" }}
      onEvents={onEvents}
      showLoading={loading}
      loadingOption={loadingOption}
      ref={(e) => setEchartsReactRef(e)}
    />
  );
};

export default Chart;
