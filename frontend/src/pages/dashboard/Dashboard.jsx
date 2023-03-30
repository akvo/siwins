import React from "react";
import { Row, Col } from "antd";

function Dashboard() {
  return (
    <div id="dashboard">
      <Row>
        <Col span={24}>
          <div>
            <h2>National Wash Data</h2>
            <p>
              Last Updated : <span>22 / 03 / 2023 </span>
            </p>
          </div>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
