import React, { useEffect, useState } from "react";
import { Row, Col, Select, Breadcrumb } from "antd";
import { api } from "../../lib";
import { UIState } from "../../state/ui";
import ChartVisual from "./components/ChartVisual";
import { Chart } from "../../components";
import AdvanceFilter from "../../components/filter";
import { generateAdvanceFilterURL } from "../../util/utils";
import { Link } from "react-router-dom";

const chartConfig = window.dashboardjson?.tabs;

const Dashboard = () => {
  const { provinceValues, barChartQuestions, advanceSearchValue } =
    UIState.useState((s) => s);
  const [chartList, setChartList] = useState([]);
  const [barChartList, setBarChartList] = useState([]);
  const [barChartData, setBarChartData] = useState([]);
  const [data, setData] = useState([]);
  const [pageLoading, setPageLoading] = useState(false);
  const [chartTitle, setChartTitle] = useState("");

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
    const find = barChartQuestions.find((f) => f.id === val);
    const chartTitleTemp = `This chart shows the distribution of  {question|${
      find?.display_name ? find?.display_name : find?.name
    }}`;
    setChartTitle(chartTitleTemp);
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
          <Row justify="space-between" align="middle">
            <Col span={24}>
              <AdvanceFilter
                prefix={
                  <Col>
                    <Breadcrumb>
                      <Breadcrumb.Item>
                        <Link to="/">Home</Link>
                      </Breadcrumb.Item>
                      <Breadcrumb.Item>Dashboard</Breadcrumb.Item>
                    </Breadcrumb>
                  </Col>
                }
                provinceValues={false}
                schoolTypeValues={false}
              />
            </Col>
          </Row>
        </Col>
        <Col span={24} align="center">
          {chartList?.map((row, index) => {
            return (
              <Row
                key={`row-${index}`}
                className="flexible-container row-wrapper"
                gutter={[10, 10]}
              >
                {row.map((r, ri) => renderColumn(r, ri))}
              </Row>
            );
          })}
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
                        height={550}
                        type={"BAR"}
                        dataZoom={false}
                        data={barChartData?.data
                          .filter((h) => !h.history)
                          .map((v) => ({
                            name: v.name,
                            value: v.value,
                            count: v.value,
                          }))}
                        wrapper={false}
                        horizontal={false}
                        showPercent={true}
                        title={chartTitle}
                        grid={{
                          top: 70,
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
