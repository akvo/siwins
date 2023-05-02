import React, { useEffect, useState } from "react";
import "./style.scss";
import { Col, Row, Button, Image, Card } from "antd";
import { ArrowDownOutlined } from "@ant-design/icons";
import { api } from "../../lib";
import { Chart } from "../../components";

const chartConfig = window.dashboardjson?.tabs;
const Home = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [chartList, setChartList] = useState([]);

  useEffect(() => {
    setLoading(true);
    const chartList = chartConfig.find(
      (item) => item.component === "OVERVIEW-CHARTS"
    )?.chartList;

    setChartList(chartList);

    const apiCall = chartList?.map((chart) => {
      const url = `chart/bar?name=${chart?.path}`;
      return api.get(url);
    });
    Promise.all(apiCall).then((res) => {
      setData(res?.map((item) => item.data).flat());
      setLoading(false);
    });
  }, []);

  const renderColumn = (cfg, index) => {
    return (
      <Col key={`col-${index}`} span={cfg?.span} className="chart-card">
        <Card>
          <Row className="chart-header" justify="space-between" align="middle">
            <h3>{cfg?.name}</h3>
          </Row>
          <Chart
            height={300}
            type="PIE"
            data={data.find((f) => f.name === cfg?.category)?.options}
            wrapper={false}
            rose={false}
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
            <Button className="explore-button">Explore Data</Button>
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
          <Col span={24} align="center">
            <Row className="flexible-container row-wrapper" gutter={[10, 10]}>
              {chartList?.map((row, index) => {
                return renderColumn(row, index);
              })}
            </Row>
          </Col>

          <Col span={8} className="icon-group">
            <Image src="/images/icons/wash.png" preview={false} />
            <h3>WASH in Schools</h3>
            <p>
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
          </Col>
          <Col span={8} className="icon-group">
            <Image src="/images/icons/jmp.png" preview={false} />
            <h3>JMP Indicators</h3>
            <p>
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
          </Col>
          <Col span={8} className="icon-group">
            <Image src="/images/icons/summary.png" preview={false} />
            <h3>National Summaries</h3>
            <p>
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
          </Col>
          <Col span={8} className="icon-group">
            <Image src="/images/icons/access.png" preview={false} />
            <h3>Access to Clean Water</h3>
            <p>
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
          </Col>
          <Col span={8} className="icon-group">
            <Image src="/images/icons/sanitation.png" preview={false} />
            <h3>Sanitation Coverage</h3>
            <p>
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
          </Col>
          <Col span={8} className="icon-group">
            <Image src="/images/icons/hygiene.png" preview={false} />
            <h3>Hygiene behaviour Change</h3>
            <p>
              Insights into the state of water sanitation and hygiene
              infrastructure in Solomon Islands with a special focus on the
              schools
            </p>
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
