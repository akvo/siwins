import {
  Easing,
  Color,
  TextStyle,
  backgroundColor,
  Icons,
  AxisLabelFormatter,
  AxisShortLabelFormatter,
  Legend,
  DataView,
  Title,
  axisTitle,
  optionToContent,
  NoData,
  downloadToExcel,
} from "./common";
import { uniq, flatten, uniqBy, isEmpty, upperFirst, sumBy } from "lodash";

const tableFormatter = (e) => {
  let table = `<table border="0" style="width:100%;border-spacing: 60px;font-size:13px;"><thead>`;
  table += `<tr><th style="font-size: 15px;color:#000;padding-bottom:8px;" colspan=${
    e?.length || 1
  }>${e[0]?.axisValueLabel || "-"}</th></tr></thead><tbody>`;
  e.filter((x) => typeof x?.value !== "undefined").map((eI) => {
    const data = eI.data;
    table += "<tr>";
    table += '<td style="width: 18px;">' + eI.marker + "</td>";
    table += '<td><span style="font-weight:500;">';
    table += upperFirst(eI.seriesName);
    table += ` (${eI.data?.year})`;
    table += "</span></td>";
    table += '<td style="width: 80px; text-align: right; font-weight: 500;">';
    table += eI.value?.toFixed(2) + "%";
    if (!isNaN(data?.count)) {
      table += ` (${data.count})`;
    }
    table += "</td>";
    table += "</tr>";
  });
  table += "</tbody></table>";
  return (
    '<div style="display:flex;align-items:center;justify-content:center">' +
    table +
    "</div>"
  );
};

const BarStack = (
  data,
  chartTitle,
  excelFile,
  extra = {},
  horizontal = false,
  highlighted = null
) => {
  if (isEmpty(data) || !data) {
    return NoData;
  }
  // Custom Axis Title
  const { xAxisTitle, yAxisTitle } = axisTitle(extra);

  const stacked =
    uniqBy(
      flatten(data.map((d) => d.stack)),
      (el) => `${el.name}${el.year ? el.year : ""}`
    ) || [];
  const xAxis = uniq(data.map((x) => x.title || x.name));
  const series = stacked.map((s) => {
    const temp = data.map((d) => {
      const vals = d.stack?.filter((c) => c.name === s.name);
      const findStack = d.stack?.find(
        (c) => c.name === s.name && c.year === s.year
      );
      return {
        name: d.name,
        value: findStack?.value,
        count: findStack?.count || 0,
        year: s.year ? s.year : "",
        itemStyle: {
          color: vals[0]?.color || s.color,
          opacity: highlighted ? (d.name === highlighted ? 1 : 0.4) : 1,
        },
        original: sumBy(vals, "value"),
        cbParam: d.name,
      };
    });
    return {
      name: s.title || s.name,
      type: "bar",
      stack: s.year ? s.year : "count",
      label: {
        show: true,
        position: "insideLeft",
        padding: 5,
        formatter: function (item) {
          const year = item.data.year;
          if (!item.value) {
            return "";
          }
          return year;
        },
      },
      color: s.color,
      data: temp,
    };
  });
  const legends = series.map((s, si) => ({
    name: s.name,
    itemStyle: { color: s.color || Color.color[si] },
  }));
  const option = {
    ...Color,
    title: {
      ...Title,
      show: !isEmpty(chartTitle),
      text: !horizontal ? chartTitle?.title : "",
      subtext: chartTitle?.subTitle,
    },
    legend: {
      ...Legend,
      data: legends,
      top: 30,
      left: "center",
    },
    grid: {
      top: 80,
      bottom: 28,
      left: 50,
      right: 30,
      show: true,
      containLabel: true,
      label: {
        color: "#222",
        ...TextStyle,
      },
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
      show: true,
      backgroundColor: "#ffffff",
      formatter: tableFormatter,
      ...TextStyle,
    },
    toolbox: {
      show: true,
      orient: "horizontal",
      right: 30,
      top: 20,
      feature: {
        saveAsImage: {
          type: "jpg",
          icon: Icons.saveAsImage,
          backgroundColor: "#EAF5FB",
        },
        dataView: {
          ...DataView,
          optionToContent: (e) =>
            optionToContent({
              option: e,
              horizontal: horizontal,
              suffix: "%",
              showPercent: true,
            }),
        },
        myDownload: {
          show: true,
          title: "Download Excel",
          icon: Icons.download,
          onclick: (e) => {
            downloadToExcel(e, excelFile, false, "%", true);
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
      max: function () {
        return 100;
      },
      axisLabel: {
        formatter: (e) => e + "%",
        ...TextStyle,
        color: "#9292ab",
      },
    },
    [horizontal ? "yAxis" : "xAxis"]: {
      data: xAxis,
      type: "category",
      name: xAxisTitle || "",
      nameTextStyle: { ...TextStyle },
      nameLocation: "middle",
      nameGap: 50,
      axisLabel: {
        width: 100,
        interval: 0,
        overflow: "break",
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
    series: series,
    ...Color,
    ...backgroundColor,
    ...Easing,
    ...extra,
  };
  return option;
};

export default BarStack;
