import React from "react";
import { Row, Col } from "antd";
import JMPGuidelines from "../../assets/files/jmp_guidelines.pdf";

const JMPDocumentation = () => {
  return (
    <div id="dashboard">
      <Row className="main-wrapper" align="center">
        <Col
          span={24}
          style={{ position: "relative", width: "100%", height: "100vh" }}
        >
          <iframe
            src={JMPGuidelines}
            title="JMP Guidelines"
            width="100%"
            height="100%"
            style={{ border: "none" }}
          />
        </Col>
      </Row>
    </div>
  );
};

export default JMPDocumentation;
