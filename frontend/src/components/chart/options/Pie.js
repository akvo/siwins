import {
  Color,
  Easing,
  TextStyle,
  backgroundColor,
  Icons,
  Title,
  Legend,
  titleFormatter,
  isTitleExist,
} from "./common";
import sumBy from "lodash/sumBy";

const Pie = (
  data,
  chartTitle,
  extra = {},
  series = {},
  showRoseChart = false,
  legend,
  grid = {}
) => {
  const noTitle = isTitleExist(chartTitle);

  data = !data ? [] : data;
  let labels = [];
  if (data.length > 0) {
    data = data.filter((x) => x.value >= 0 || x.count >= 0);
    labels = data.map((x) => x.name);
    let total = sumBy(data, "count");
    if (data[0]?.total) {
      // for custom percentage calculation (percentage should keep the correct value after filtering)
      total = data[0]?.total;
    }
    data = data.map((x) => {
      const percentage = ((x.value / total) * 100)?.toFixed(2) || 0;
      return {
        ...x,
        value: x.count,
        percentage: percentage,
      };
    });
  }
  const { textStyle } = TextStyle;
  const rose = {};

  const option = {
    title: {
      ...Title,
      show: !noTitle,
      text: titleFormatter(chartTitle?.title),
      subtext: titleFormatter(chartTitle?.subTitle),
    },
    grid: {
      top: grid?.top ? grid.top : 0,
      bottom: grid?.bottom ? grid.bottom : 0,
      left: grid?.left ? grid.left : 0,
      right: grid?.right ? grid.right : 0,
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
      top: noTitle ? 50 : 88,
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
          formatter: function (p) {
            // custom percentage
            if (data[0]?.total) {
              return p?.data?.percentage ? `${p.data.percentage}%` : "0%";
            }
            return `${p.percent}%`;
          },
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
        top: noTitle ? 10 : 50,
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
