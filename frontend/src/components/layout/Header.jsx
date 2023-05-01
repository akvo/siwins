import React from "react";
import { Row, Col, Space, Image } from "antd";
import { Link } from "react-router-dom";

const Header = ({ className = "header" }) => {
  return (
    <Row className={className} align="middle" justify="space-between">
      <Col className="left">
        <Space size="large" align="center">
          <div className="brand">
            <Link to="/">
              <Image src="/images/logo.png" preview={false} />
            </Link>
          </div>
        </Space>
      </Col>
      <Col className="right">
        <Space size="large" align="center">
          <div>
            <Link to="/dashboard/maps">Maps</Link>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/documentation">Documentation</Link>
          </div>
        </Space>
      </Col>
    </Row>
  );
};

export default Header;
