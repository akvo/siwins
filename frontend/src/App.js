import React from "react";
import { Layout, Menu } from "antd";
import "./App.css";

const { Header, Footer, Content } = Layout;

const App = () => {
  return (
    <Layout className="layout">
      <Header className="site-layout-header">
        <div className="logo" />
        <Menu
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
        />
      </Header>
      <Content className="site-layout-content">Content</Content>
      <Footer className="site-layout-footer">
        SI-WINS ©2022 Created by <strong>Akvo</strong>
      </Footer>
    </Layout>
  );
};

export default App;
