import React from "react";
import { Column } from "@ant-design/plots";
import { chain, groupBy, orderBy } from "lodash";
import { Collapse } from "antd";

const { Panel } = Collapse;

const RenderChart = ({ data }) => {
  // get sample data to find question type
  const sample = data?.[0] || {};
  const qtype = sample?.type;
  data = orderBy(
    data.map((d) => ({
      value: d.value,
      date: d.date?.split(" - ").join("\n"),
    })),
    ["date"],
    "desc"
  );
  let config = {
    data,
    color: "#00b96b",
    // legend: {
    //   position: "top-left",
    // },
  };
  switch (qtype) {
    case "option":
      return null;
    default:
      config = {
        ...config,
        xField: "date",
        yField: "value",
        label: {
          position: "middle",
          // 'top', 'bottom', 'middle',
          style: {
            fill: "#FFFFFF",
            opacity: 0.9,
          },
        },
        xAxis: {
          label: {
            autoHide: true,
            autoRotate: true,
          },
        },
        minColumnWidth: 10,
        maxColumnWidth: 50,
      };
      return <Column {...config} />;
  }
};

const Chart = ({ activePanel, setActivePanel, chartData }) => {
  const { monitoring } = chartData;
  const grouped = chain(
    groupBy(
      monitoring.filter((d) => d.type === "number"),
      "question"
    )
  ).value();

  return (
    <Collapse
      activeKey={[activePanel]}
      onChange={setActivePanel}
      accordion={true}
    >
      {Object.keys(grouped).map((key, ki) => {
        return (
          <Panel header={key} key={ki + 1}>
            <RenderChart data={grouped?.[key] || []} />
          </Panel>
        );
      })}
    </Collapse>
  );
};

export default Chart;
