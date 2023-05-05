import {
  Color,
  Easing,
  TextStyle,
  backgroundColor,
  Icons,
  Title,
  Legend,
} from "./common";
import { isEmpty, sumBy } from "lodash";

const Pie = (
  data,
  chartTitle,
  extra = {},
  series = {},
  showRoseChart = false,
  legend
) => {
  data = !data ? [] : data;
  let labels = [];
  if (data.length > 0) {
    data = data.filter((x) => x.value >= 0 || x.count >= 0);
    labels = data.map((x) => x.name);
    const total = sumBy(data, "count");
    data = data.map((x) => ({
      ...x,
      value: x.count,
      percentage: ((x.value / total) * 100)?.toFixed(0) || 0,
    }));
  }
  const { textStyle } = TextStyle;
  const rose = {};

  const option = {
    title: {
      ...Title,
      show: !isEmpty(chartTitle),
      text: chartTitle?.title,
      subtext: chartTitle?.subTitle,
    },
    tooltip: {
      show: true,
      trigger: "item",
      formatter: "{b}",
      padding: 5,
      backgroundColor: "#f2f2f2",
      textStyle: {
        ...textStyle,
        fontSize: 12,
      },
    },
    toolbox: {
      show: true,
      showTitle: true,
      orient: "horizontal",
      right: 10,
      top: 80,
      feature: {
        saveAsImage: {
          type: "jpg",
          title: "Save Image",
          icon: Icons.saveAsImage,
          backgroundColor: "#EAF5FB",
        },
      },
    },
    series: [
      {
        name: "main",
        type: "pie",
        avoidLabelOverlap: true,
        ...(showRoseChart && { roseType: "area" }),
        label: {
          show: true,
          formatter: "{d}%",
          fontSize: 12,
          fontWeight: "bold",
        },
        startAngle: 0,
        radius: ["15%", "50%"],
        center: ["50%", "57%"],
        data: data.map((v, vi) => ({
          ...v,
          itemStyle: { color: v.color || Color.color[vi] },
        })),
        ...series,
        ...rose,
      },
    ],
    ...(legend && {
      legend: {
        data: labels,
        ...Legend,
        top: 30,
        left: "center",
      },
    }),
    ...Color,
    ...backgroundColor,
    ...Easing,
    ...extra,
  };
  return option;
};

export default Pie;
