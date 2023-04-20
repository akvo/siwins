import {
  Color,
  Easing,
  TextStyle,
  backgroundColor,
  Icons,
  Title,
} from "./common";
import { isEmpty, sumBy } from "lodash";

const Pie = (data, chartTitle, extra = {}, series = {}) => {
  data = !data ? [] : data;
  if (data.length > 0) {
    data = data.filter((x) => x.value >= 0);
    const total = sumBy(data, "value");
    data = data.map((x) => ({
      ...x,
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
      right: 30,
      top: 10,
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
        roseType: "area",
        avoidLabelOverlap: true,
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
    legend: { show: false },
    ...Color,
    ...backgroundColor,
    ...Easing,
    ...extra,
  };
  return option;
};

export default Pie;
