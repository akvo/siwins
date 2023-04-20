import React from "react";
import { Row, Col } from "antd";
import { Map } from "../../components";
import AdvanceFilter from "../../components/filter";

function Maps() {
  return (
    <div id="map">
      <Row>
        <Col span={24}>
          <AdvanceFilter />
        </Col>
      </Row>
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
