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
import { sortBy, isEmpty, sumBy, uniqBy, flatten } from "lodash";

const Bar = (
  data,
  chartTitle,
  excelFile,
  extra = {},
  legend = {},
  horizontal = false,
  grid = {},
  dataZoom,
  history,
  reduceHistoryValue = true,
  showPercent = true
) => {
  if (isEmpty(data) || !data) {
    return NoData;
  }
  // Custom Axis Title
  const { xAxisTitle, yAxisTitle } = axisTitle(extra);
  if (showPercent) {
    const total = sumBy(data, "value");
    data = sortBy(data, "order");
    data = data.map((x) => ({ ...x, percentage: (x.value / total) * 100 }));
  }
  let result = [];
  let labels = data.map((x) => x.name);
  if (history) {
    result = [
      ...data
        .reduce((c, { year, name, value, color, count }) => {
          if (!c.has(year)) {
            c.set(year, { year, name: year, type: "bar", data: [] });
          }
          c.get(year).data.push({
            name: name,
            count: count,
            value: value,
            itemStyle: {
              color: color,
            },
            label: {
              show: true,
              position: "insideLeft",
              formatter: function () {
                return year;
              },
            },
          });
          return c;
        }, new Map())
        .values(),
    ].map((item) => {
      return {
        ...item,
        data: item.data.map((d) => {
          let value = d.value;
          if (reduceHistoryValue) {
            value = +(
              (d.value / item.data.reduce((a, c) => a + c.value, 0)) *
              100
            ).toFixed(2);
          }
          return {
            ...d,
            value: value,
          };
        }),
      };
    });
    labels = uniqBy(flatten(data), "name").map((x) => x.name);
  }

  const option = {
    ...Color,
    title: {
      ...Title,
      show: !isEmpty(chartTitle),
      text: !horizontal ? chartTitle?.title : "",
      subtext: chartTitle?.subTitle,
    },
    grid: {
      top: grid?.top ? grid.top : horizontal ? 80 : 20,
      bottom: grid?.bottom ? grid.bottom : horizontal ? 28 : 20,
      left: grid?.left ? grid.left : horizontal ? 100 : 50,
      right: grid?.right ? grid.right : horizontal ? 30 : 30,
      show: true,
      label: {
        color: "#222",
        ...TextStyle,
      },
    },
    tooltip: {
      show: true,
      trigger: "item",
      padding: 5,
      backgroundColor: "#f2f2f2",
      formatter: (s) => {
        const val = showPercent ? `${s.data.count} (${s.value}%)` : s.value;
        return `${s.marker} <b>${s.name}</b>:       ${val}`;
      },
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
            optionToContent({
              option: e,
              horizontal: horizontal,
              suffix: showPercent ? "%" : "",
              showPercent: showPercent,
            }),
        },
        myDownload: {
          show: true,
          title: "Download Excel",
          icon: Icons.download,
          onclick: (e) => {
            const suffix = showPercent ? "%" : "";
            downloadToExcel(e, excelFile, chartTitle, suffix, showPercent);
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
      ...(horizontal && { inverse: true }),
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
    series: history
      ? result
      : [
          {
            data: data.map((v, vi) => ({
              name: v.name,
              value: showPercent ? v.percentage?.toFixed(2) : v.value,
              count: v.count,
              itemStyle: { color: v.color || Color.color[vi] },
            })),
            type: "bar",
            barMaxWidth: 50,
            label: {
              colorBy: "data",
              position: horizontal ? "insideLeft" : "top",
              show: true,
              padding: 5,
              backgroundColor: "rgba(0,0,0,.3)",
              ...TextStyle,
              color: "#fff",
              formatter: (s) => {
                return showPercent ? `${s.data.count} (${s.value} %)` : s.value;
              },
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
