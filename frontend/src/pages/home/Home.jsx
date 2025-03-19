import React, { useEffect, useState, useRef } from "react";
import "./style.scss";
import { Col, Row, Button, Image, Card, Statistic } from "antd";
import { ArrowDownOutlined } from "@ant-design/icons";
import { api, ds } from "../../lib";
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
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [chartList, setChartList] = useState([]);
  const target = useRef(null);

  useEffect(() => {
    const dsKey = "/home/chart/bar?name=overview-charts";
    setLoading(true);

    const chartList = chartConfig.find(
      (item) => item.component === "OVERVIEW-CHARTS"
    )?.chartList;
    setChartList(chartList);

    // ** fetch data from indexed DB first
    ds.getSource(dsKey).then((cachedData) => {
      if (!cachedData) {
        const apiCall = chartList?.map((chart) => {
          const url = `chart/bar?name=${chart?.path}`;
          return api.get(url);
        });
        sequentialPromise(apiCall).then((res) => {
          const dataTemp = res.map((r) => r.data).flat();
          ds.saveSource({ endpoint: dsKey, data: dataTemp });
          setData(dataTemp);
          setLoading(false);
        });
      } else {
        setData(cachedData.data);
        setLoading(false);
      }
    });
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
            height={350}
            type="PIE"
            data={findData?.options}
            wrapper={false}
            showRoseChart={false}
            legend={true}
            loading={loading}
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
            <Button
              type="text"
              className="scroll-button"
              onClick={() =>
                target.current?.scrollIntoView({
                  behavior: "smooth",
                  block: "start",
                })
              }
            >
              Scroll
              <ArrowDownOutlined />
            </Button>
          </Col>
        </Row>
        <Row align="middle" justify="center">
          <Col
            style={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              maxWidth: 1200,
            }}
          >
            <Image src="/images/home.png" preview={false} width="90%" />
          </Col>
        </Row>
      </section>
      <section className="metrics-section container" ref={target}>
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
          <Col span={24} align="center">
            <p>
              For <b>province and year wise breakdowns</b> please visit the{" "}
              <a style={{ color: "#3FB8EC" }} href="/dashboard">
                dashboard
              </a>
            </p>
          </Col>
        </Row>
      </section>
      <section className="about-section container">
        <Row align="middle" justify="center">
          <Col>
            <Image src="/images/unicef-logo.png" preview={false} />
            <p className="about-content">
              Elevating our commitment to data-driven evidence, we&apos;re
              bolstering evidence-based budgeting and planning for WASH in
              Schools, thanks to insights from the Data Explorer
            </p>
            <p>
              - Ministry of Education and Human Resources Development, Solomon
              Islands Government
            </p>
            <div className="info-content">
              <Image src="/images/mehrd_logo_no_bg.png" preview={false} />
            </div>
          </Col>
        </Row>
      </section>
    </div>
  );
};

export default Home;
