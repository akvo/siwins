import React, { useEffect, useState } from "react";
import { Row, Col, Card } from "antd";
import { api } from "../../lib";
import { UIState } from "../../state/ui";
import { Chart } from "../../components";

const chartConfig = window.dashboardjson?.tabs;

const Dashboard = () => {
  const { provinceValues } = UIState.useState((s) => s);
  const [chartData, setChartData] = useState([]);
  const [chartList, setChartList] = useState([]);
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
    Promise.all(apiCall)
      .then((res) => {
        const allData = res?.map((r) => {
          const chartSetting = chartList?.find(
            (c) => c.path === r?.data?.question
          );
          const data = provinceValues.map((adm) => {
            const findData = r?.data?.data?.find(
              (d) => d.administration === adm.name
            );
            const stack = findData?.child?.map((c, cx) => {
              return {
                id: cx,
                name: c.option,
                color: c.color,
                order: cx + 1,
                score: 0,
                code: null,
                translations: null,
                value: c.percent,
              };
            });
            return {
              ...adm,
              score: findData?.score,
              stack: stack,
            };
          });
          return {
            name: r?.data?.question,
            type: chartSetting?.type,
            data: data,
          };
        });
        return allData;
      })
      .then((res) => {
        setChartData(res);
        setPageLoading(false);
      });
  }, [provinceValues]);

  return (
    <div id="dashboard">
      <Row>
        <Col span={24}>
          <div>
            <h2>National Wash Data</h2>
            <p>
              Last Updated : <span>22 / 03 / 2023 </span>
            </p>
          </div>
        </Col>
      </Row>
      {!pageLoading &&
        chartList &&
        chartList?.map((item, index) => (
          <Row key={index}>
            {item?.map((col) => (
              <Col key={col?.title} span={col.span}>
                <Card>
                  <Chart
                    height={50 * chartData.length + 188}
                    type="BARSTACK"
                    data={chartData.find((f) => f.name === col.path)?.data}
                    wrapper={false}
                    horizontal={true}
                    series={{ left: "10%" }}
                    loading={pageLoading}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        ))}
    </div>
  );
};

export default Dashboard;
