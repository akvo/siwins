import React from "react";
import { Row, Col } from "antd";
import { Map } from "../../components";

function Maps() {
  return (
    <div>
      <Row>
        <Col span={24}>
          <div className="map-wrapper">
            <Map />
          </div>
        </Col>
      </Row>
    </div>
  );
}

export default Maps;
