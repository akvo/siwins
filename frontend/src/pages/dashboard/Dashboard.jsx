/* eslint-disable react-hooks/exhaustive-deps */
import React, { useEffect, useState } from "react";
import { Row, Col, Select, Breadcrumb } from "antd";
import { api } from "../../lib";
import { UIState } from "../../state/ui";
import ChartVisual from "./components/ChartVisual";
import { Chart } from "../../components";
import AdvanceFilter from "../../components/filter";
import {
  generateAdvanceFilterURL,
  generateFilterURL,
  sequentialPromise,
} from "../../util/utils";
import { Link } from "react-router-dom";
import { orderBy } from "lodash";

const chartConfig = window.dashboardjson?.tabs;

const Dashboard = () => {
  const {
    provinceValues,
    barChartQuestions,
    advanceSearchValue,
    schoolTypeValues,
    provinceFilterValue,
  } = UIState.useState((s) => s);
  const [chartList, setChartList] = useState([]);
  const [barChartList, setBarChartList] = useState([]);
  const [barChartData, setBarChartData] = useState([]);
  const [data, setData] = useState([]);
  const [pageLoading, setPageLoading] = useState(false);
  const [chartTitle, setChartTitle] = useState("");
  const [selectedIndicator, setSelectedIndicator] = useState("");

  const handleProvinceFilter = (value) => {
    UIState.update((s) => {
      s.provinceFilterValue = {
        ...s.provinceFilterValue,
        selectedProvince: value,
      };
    });
  };

  const handleSchoolTypeFilter = (value) => {
    UIState.update((s) => {
      s.provinceFilterValue = {
        ...s.provinceFilterValue,
        selectedSchoolType: value,
      };
    });
  };

  // jmp chart data
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
      url = generateFilterURL(provinceFilterValue, url);
      return api.get(url);
    });
    sequentialPromise(apiCall).then((res) => {
      setData(res);
      setPageLoading(false);
    });
  }, [advanceSearchValue, provinceFilterValue]);

  // generic bar chart
  useEffect(() => {
    if (!selectedIndicator) {
      setBarChartData([]);
    } else {
      let url = `chart/generic-bar/${selectedIndicator}`;
      url = generateAdvanceFilterURL(advanceSearchValue, url);
      url = generateFilterURL(provinceFilterValue, url);
      api
        .get(url)
        .then((res) => {
          setBarChartData(res.data);
        })
        .catch((e) => console.error(e));
    }
  }, [selectedIndicator, advanceSearchValue, provinceFilterValue]);

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

  useEffect(() => {
    if (barChartData.length === 0) {
      handleOnChangeQuestionDropdown(barChartQuestions?.[0]?.id);
    }
  }, [barChartQuestions, barChartData]);

  const handleOnChangeQuestionDropdown = (val) => {
    setSelectedIndicator(val);
    const find = barChartQuestions.find((f) => f.id === val);
    setChartTitle(find?.display_name ? find?.display_name : find?.name);
  };

  return (
    <div id="dashboard">
      <Row className="main-wrapper" align="center">
        <Col span={24}>
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
                provinceValues={provinceValues}
                schoolTypeValues={schoolTypeValues}
                handleSchoolTypeFilter={handleSchoolTypeFilter}
                handleProvinceFilter={handleProvinceFilter}
                selectedProvince={provinceFilterValue?.selectedProvince}
                selectedSchoolType={provinceFilterValue?.selectedSchoolType}
              />
            </Col>
          </Row>
        </Col>
        <Col span={24} align="center" style={{ padding: "20px 30px" }}>
          {orderBy(chartList, ["order"], ["asc"])?.map((row, index) => {
            return (
              <Row
                key={`row-${index}`}
                className="flexible-container row-wrapper"
                gutter={[10, 10]}
              >
                {renderColumn(row, index)}
              </Row>
            );
          })}
        </Col>
      </Row>
      <Row className="bar-chart-wrapper" align="center">
        <Col span={24} align="center">
          <div className="header-container">
            <h3>Bar Chart for Indicator</h3>
          </div>
        </Col>
        <Col span={24} align="center">
          <div className="chart-wrapper">
            <Select
              dropdownMatchSelectWidth={false}
              placement={"bottomLeft"}
              showSearch
              allowClear
              value={selectedIndicator}
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
              orderBy(barChartList, ["order"], ["asc"])?.map((row) => {
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
                        title={`This chart shows the distribution of  {question|${chartTitle}}`}
                        extra={{
                          axisTitle: {
                            x: [chartTitle || null],
                            y: "Percentage",
                          },
                        }}
                        excelFile={chartTitle}
                        grid={{
                          top: "25%",
                          right: "5%",
                          left: "5%",
                          bottom: "15%",
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
