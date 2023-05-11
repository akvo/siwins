import React, { useEffect, useState } from "react";
import "./style.scss";
import { Col, Row, Button, Image, Card, Statistic } from "antd";
import { ArrowDownOutlined } from "@ant-design/icons";
import { api } from "../../lib";
import { Chart } from "../../components";
import CountUp from "react-countup";
import { UIState } from "../../state/ui";
import { Link } from "react-router-dom";
import { orderBy } from "lodash";
import { sequentialPromise } from "../../util/utils";

const chartConfig = window.dashboardjson?.tabs;

const formatter = (value) => <CountUp end={value} duration={2} separator="," />;

const Home = () => {
  const { schoolTotal } = UIState.useState((s) => s);
  const [chartList, setChartList] = useState([]);
  const [data, setData] = useState([]);

  useEffect(() => {
    // setLoading(true);
    const chartList = chartConfig.find(
      (item) => item.component === "OVERVIEW-CHARTS"
    )?.chartList;
    setChartList(chartList);

    const apiCall = chartList?.map((chart) => {
      const url = `chart/bar?name=${chart?.path}`;
      return api.get(url);
    });
    sequentialPromise(apiCall).then((res) => setData(res));
  }, []);

  const renderColumn = (cfg, index) => {
    const findData = data?.find((f) => f.category === cfg?.path);
    return (
      <Col key={`col-${index}`} span={cfg?.span} className="chart-card">
        <Card>
          <Row className="chart-header" justify="center" align="middle">
            <h3>{cfg?.title}</h3>
          </Row>
          <Chart
            height={300}
            type="PIE"
            data={findData?.options}
            wrapper={false}
            showRoseChart={false}
            legend={true}
            loading={!findData}
          />
        </Card>
      </Col>
    );
  };

  return (
    <div id="home">
      <section className="home-landing container">
        <Row>
          <Col className="intro-text" span={12}>
            <h1>Solomon Islands WASH in Schools Data Explorer</h1>
            <p>
              Insights into the state of water sanitation and hygiene <br />
              in the schools of Solomon Islands
            </p>
          </Col>
        </Row>
        <Row align="middle" justify="space-between" className="explore-row">
          <Col span={12}>
            <Link to="/dashboard/maps">
              <Button className="explore-button">Explore Data</Button>
            </Link>
          </Col>
          <Col span={12} style={{ textAlign: "end" }}>
            <Button type="text" className="scroll-button">
              Scroll
              <ArrowDownOutlined />
            </Button>
          </Col>
        </Row>
        <Row align="middle" justify="center">
          <Col>
            <Image src="/images/home.png" preview={false} />
          </Col>
        </Row>
      </section>
      <section className="metrics-section container">
        <Row align="middle" justify="center">
          <Col span={10}>
            <p className="title">Key Metrics</p>
            <h2>WASH in Schools Analytics</h2>
            <p className="content">
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
          </Col>
        </Row>
        <Row justify="space-between" align="middle" gutter={[48, 48]}>
          <Col span={24} style={{ textAlign: "center" }}>
            <Statistic
              title={<h3>Number of schools</h3>}
              value={schoolTotal}
              formatter={formatter}
            />
          </Col>
          <Col span={24} align="center">
            <Row className="flexible-container row-wrapper" gutter={[10, 10]}>
              {orderBy(chartList, ["order"], ["asc"])?.map((row, index) => {
                return renderColumn(row, index);
              })}
            </Row>
          </Col>
        </Row>
      </section>
      <section className="about-section container">
        <Row align="middle" justify="center">
          <Col>
            <Image src="/images/unicef-logo.png" preview={false} />
            <p className="about-content">
              We are able to monitor the performance of our projects across the
              country thanks to the data explorer
            </p>
            <div className="info-content">
              <Image src="/images/about.png" preview={false} />
              <h3>Jeremy Abula</h3>
              <p>Programme Manager, UNICEF</p>
            </div>
          </Col>
        </Row>
      </section>
    </div>
  );
};

export default Home;
