import React, { useEffect, useState } from "react";
import { Row, Col } from "antd";
import { api } from "../../lib";
import { UIState } from "../../state/ui";
import ChartVisual from "./components/ChartVisual";

const chartConfig = window.dashboardjson?.tabs;

const Dashboard = () => {
  const { provinceValues } = UIState.useState((s) => s);
  const [chartList, setChartList] = useState([]);
  const [data, setData] = useState([]);
  const [pageLoading, setPageLoading] = useState(false);

  useEffect(() => {
    const chartList = chartConfig
      .find((item) => item.component === "JMP-CHARTS")
      ?.chartList.flat();
    setChartList(
      chartConfig.find((item) => item.component === "JMP-CHARTS")?.chartList
    );
    setPageLoading(true);
    const apiCall = chartList?.map((chart) => {
      const url = `chart/jmp-data/${chart?.path}`;
      return api.get(url);
    });
    Promise.all(apiCall).then((res) => {
      setData(res);
      setPageLoading(false);
    });
  }, []);

  const renderColumn = (cfg, index) => {
    return (
      <ChartVisual
        key={index}
        chartConfig={{
          ...cfg,
          data: data,
          index: index,
          provinceValues: provinceValues,
        }}
        loading={pageLoading}
      />
    );
  };

  return (
    <div id="dashboard">
      <Row className="main-wrapper" align="center">
        <Col span={24} align="center">
          {!pageLoading && chartList ? (
            chartList?.map((row, index) => {
              return (
                <Row
                  key={`row-${index}`}
                  className="flexible-container row-wrapper"
                  gutter={[10, 10]}
                >
                  {row.map((r, ri) => renderColumn(r, ri))}
                </Row>
              );
            })
          ) : (
            <h4>No data</h4>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
