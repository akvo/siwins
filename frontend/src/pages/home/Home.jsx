import React from "react";
import "./style.scss";
import { Col, Row, Button, Image } from "antd";
import { ArrowDownOutlined } from "@ant-design/icons";

const Home = () => {
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
    </div>
  );
};

export default Home;
