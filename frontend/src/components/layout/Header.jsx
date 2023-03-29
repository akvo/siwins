import React from "react";
import { Row, Col, Space, Button, Image } from "antd";
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
            <Button type="link" size="large">
              Maps
            </Button>
            <Button type="link" size="large">
              Dashboard
            </Button>
            <Button type="link" size="large">
              Documentation
            </Button>
          </div>
        </Space>
      </Col>
    </Row>
  );
};

export default Header;
