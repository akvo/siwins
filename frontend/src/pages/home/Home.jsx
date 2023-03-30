import React from "react";
import "./style.scss";
import { Col, Row, Button } from "antd";
import { ArrowDownOutlined } from "@ant-design/icons";

const Home = () => {
  return (
    <div id="home" className="container">
      <Row className="home-landing">
        <Col className="intro-text" span={12}>
          <h1>Solomon Islands WASH in Schools Data Explorer</h1>
          <p>
            Insights into the state of water sanitation and hygiene <br />
            in the schools of Solomon Islands
          </p>
        </Col>
      </Row>
      <Row align="middle" justify="space-between">
        <Col span={12}>
          <Button className="explore-button">Explore Data</Button>
        </Col>
        <Col span={12} style={{ textAlign: "end" }}>
          <Button type="text" className="scroll-button">
            Scroll
          </Button>
          <ArrowDownOutlined />
        </Col>
      </Row>
    </div>
  );
};

export default Home;
