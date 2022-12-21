import React from "react";
import "./App.css";
import { Row, Col, Layout } from "antd";
import { Map } from "./components";
import AdvanceFilter from "./components/filter";

const { Header, Footer, Content } = Layout;

const App = () => {
  return (
    <Layout className="layout">
      <AdvanceFilter />
      <Header className="site-layout-header">
        <div className="logo">
          <h1>SI-WINS</h1>
        </div>
        {/* <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={["2"]}
          items={new Array(3).fill(null).map((_, index) => {
            const key = index + 1;
            return {
              key,
              label: `nav ${key}`,
            };
          })}
        /> */}
      </Header>
      <Content className="site-layout-content">
        <Row>
          <Col span={24}>
            <div className="map-wrapper">
              <Map />
            </div>
          </Col>
        </Row>
      </Content>
      <Footer className="site-layout-footer">
        SI-WINS ©2022 Created by <strong>Akvo</strong>
      </Footer>
    </Layout>
  );
};

export default App;
