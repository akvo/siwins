import React, { useEffect, useState } from "react";
import { Row, Col, Select } from "antd";
import { api } from "../../lib";
import { UIState } from "../../state/ui";
import ChartVisual from "./components/ChartVisual";
import { Chart } from "../../components";
import AdvanceFilter from "../../components/filter";
import { generateAdvanceFilterURL } from "../../util/utils";

const chartConfig = window.dashboardjson?.tabs;

const Dashboard = () => {
  const { provinceValues, barChartQuestions, advanceSearchValue } =
    UIState.useState((s) => s);
  const [chartList, setChartList] = useState([]);
  const [barChartList, setBarChartList] = useState([]);
  const [barChartData, setBarChartData] = useState([]);
  const [data, setData] = useState([]);
  const [pageLoading, setPageLoading] = useState(false);

  useEffect(() => {
    const chartList = chartConfig
      .find((item) => item.component === "JMP-CHARTS")
      ?.chartList.flat();
    setChartList(
      chartConfig.find((item) => item.component === "JMP-CHARTS")?.chartList
    );
    setBarChartList(
      chartConfig.find((item) => item.component === "GENERIC-CHART-GROUP")
        ?.chartList
    );
    setPageLoading(true);
    const apiCall = chartList?.map((chart) => {
      let url = `chart/jmp-data/${chart?.path}`;
      url = generateAdvanceFilterURL(advanceSearchValue, url);
      return api.get(url);
    });
    Promise.all(apiCall).then((res) => {
      setData(res);
      setPageLoading(false);
    });
  }, [advanceSearchValue]);

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

  const handleOnChangeQuestionDropdown = (val) => {
    if (val) {
      const url = `chart/generic-bar/${val}`;
      api
        .get(url)
        .then((res) => {
          setBarChartData(res.data);
        })
        .catch((e) => console.error(e));
    } else {
      setBarChartData([]);
    }
  };

  return (
    <div id="dashboard">
      <Row className="main-wrapper" align="center">
        <Col span={24} style={{ marginBottom: 20 }}>
          <AdvanceFilter provinceValues={false} schoolTypeValues={false} />
        </Col>
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
      <Row className="bar-chart-wrapper" align="center">
        <Col span={24} align="center">
          <div className="header-container">
            <h3>Bar Chart for Any Indicator</h3>
          </div>
        </Col>
        <Col span={24} align="center">
          <div className="chart-wrapper">
            <Select
              dropdownMatchSelectWidth={false}
              placement={"bottomLeft"}
              showSearch
              allowClear
              placeholder="Select question"
              optionFilterProp="children"
              filterOption={(input, option) =>
                (option?.label ?? "")
                  .toLowerCase()
                  .includes(input.toLowerCase())
              }
              options={barChartQuestions?.map((q) => ({
                label: q?.display_name ? q?.display_name : q.name,
                value: q.id,
              }))}
              onChange={(val) => handleOnChangeQuestionDropdown(val)}
            />
            {barChartData?.data?.length > 0 &&
              barChartList?.map((row) => {
                return (
                  <Row
                    key={`row-${row.name}`}
                    className="flexible-container row-wrapper"
                    gutter={[10, 10]}
                  >
                    <Col span={24}>
                      <Chart
                        height={50 * barChartData?.data.length + 188}
                        type={"BAR"}
                        dataZoom={false}
                        data={barChartData?.data.map((v) => ({
                          name: v.name,
                          value: v.value,
                          count: v.value,
                        }))}
                        wrapper={false}
                        horizontal={false}
                        grid={{
                          top: 70,
                          left: 120,
                        }}
                      />
                    </Col>
                  </Row>
                );
              })}
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
