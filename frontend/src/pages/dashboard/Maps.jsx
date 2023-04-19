import React from "react";
import { Row, Col } from "antd";
import { Map } from "../../components";
import AdvanceFilter from "../../components/filter";

function Maps() {
  return (
    <div id="map">
      <Row>
        <Col span={24}>
          <div className="title-wrapper">
            <h2>National Map</h2>
            <p>
              Last Updated : <span>22 / 03 / 2023 </span>
            </p>
          </div>
        </Col>
      </Row>
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
