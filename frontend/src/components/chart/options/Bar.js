import {
  Easing,
  Color,
  TextStyle,
  backgroundColor,
  Icons,
  AxisLabelFormatter,
  AxisShortLabelFormatter,
  Title,
  axisTitle,
  DataView,
  optionToContent,
  NoData,
  downloadToExcel,
} from "./common";
import { sortBy, isEmpty, sumBy } from "lodash";

const Bar = (
  data,
  chartTitle,
  excelFile,
  extra = {},
  legend = {},
  horizontal = false,
  grid = {},
  dataZoom
) => {
  if (isEmpty(data) || !data) {
    return NoData;
  }

  // Custom Axis Title
  const { xAxisTitle, yAxisTitle } = axisTitle(extra);
  const total = sumBy(data, "value");
  data = sortBy(data, "order");
  data = data.map((x) => ({ ...x, percentage: (x.value / total) * 100 }));
  const labels = data.map((x) => x.name);
  const option = {
    ...Color,
    title: {
      ...Title,
      show: !isEmpty(chartTitle),
      text: chartTitle?.title,
      subtext: chartTitle?.subTitle,
    },
    grid: {
      top: grid?.top ? grid.top : horizontal ? 80 : 20,
      bottom: grid?.bottom ? grid.bottom : horizontal ? 28 : 20,
      left: grid?.left ? grid.left : horizontal ? 100 : 0,
      right: grid?.right ? grid.right : horizontal ? 20 : 0,
      show: true,
      label: {
        color: "#222",
        ...TextStyle,
      },
    },
    tooltip: {
      show: true,
      trigger: "item",
      formatter: '<div class="no-border">{b}</div>',
      padding: 5,
      backgroundColor: "#f2f2f2",
      ...TextStyle,
    },
    toolbox: {
      show: true,
      showTitle: true,
      orient: "horizontal",
      right: 30,
      top: 20,
      feature: {
        saveAsImage: {
          type: "jpg",
          title: "Save Image",
          icon: Icons.saveAsImage,
          backgroundColor: "#EAF5FB",
        },
        dataView: {
          ...DataView,
          optionToContent: (e) =>
            optionToContent({ option: e, horizontal: horizontal, suffix: "%" }),
        },
        myDownload: {
          show: true,
          title: "Download Excel",
          icon: Icons.download,
          onclick: (e) => {
            downloadToExcel(e, excelFile);
          },
        },
      },
    },
    [horizontal ? "xAxis" : "yAxis"]: {
      type: "value",
      name: yAxisTitle || "",
      nameTextStyle: { ...TextStyle },
      nameLocation: "middle",
      nameGap: 50,
      axisLabel: {
        ...TextStyle,
        color: "#9292ab",
      },
    },
    [horizontal ? "yAxis" : "xAxis"]: {
      type: "category",
      data: labels,
      name: xAxisTitle || "",
      nameTextStyle: { ...TextStyle },
      nameLocation: "middle",
      nameGap: 50,
      axisLabel: {
        width: horizontal ? 90 : "auto",
        overflow: horizontal ? "break" : "none",
        interval: 0,
        ...TextStyle,
        color: "#4b4b4e",
        formatter: horizontal
          ? AxisShortLabelFormatter?.formatter
          : AxisLabelFormatter?.formatter,
      },
      axisTick: {
        alignWithLabel: true,
      },
    },
    dataZoom: dataZoom,
    series: [
      {
        data: data.map((v, vi) => ({
          name: v.name,
          value: v.value,
          count: v.count,
          itemStyle: { color: v.color || Color.color[vi] },
        })),
        type: "bar",
        barMaxWidth: 20,
        label: {
          colorBy: "data",
          position: horizontal ? "insideLeft" : "top",
          show: true,
          padding: 5,
          backgroundColor: "rgba(0,0,0,.3)",
          ...TextStyle,
          color: "#fff",
        },
      },
    ],
    ...Color,
    ...backgroundColor,
    ...Easing,
    ...extra,
    ...legend,
  };
  return option;
};

export default Bar;
