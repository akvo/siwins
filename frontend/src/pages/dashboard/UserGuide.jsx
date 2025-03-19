import React from "react";
import { Row, Col } from "antd";
import UserGuideDoc from "../../assets/files/si-wins-user-guide.pdf";

const UserGuide = () => {
  return (
    <div id="dashboard">
      <Row className="main-wrapper" align="center">
        <Col
          span={24}
          style={{ position: "relative", width: "100%", height: "100vh" }}
        >
          <iframe
            src={UserGuideDoc}
            title="User Guide"
            width="100%"
            height="100%"
            style={{ border: "none" }}
          />
        </Col>
      </Row>
    </div>
  );
};

export default UserGuide;
