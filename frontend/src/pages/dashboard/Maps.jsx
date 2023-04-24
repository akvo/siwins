import React, { useState } from "react";
import { Row, Col } from "antd";
import { Map } from "../../components";
import AdvanceFilter from "../../components/filter";
import { UIState } from "../../state/ui";

function Maps() {
  const [selectedProvince, setSelectedProvince] = useState(["All"]);
  const [selectedSchoolType, setSelectedSchoolType] = useState(["All"]);
  const { provinceValues, schoolTypeValues } = UIState.useState((s) => s);

  const handleProvinceFilter = (value) => {
    if (value === "disable") {
      setSelectedProvince(provinceValues.map((item) => item.name));
      return;
    }
    if (value === "all") {
      setSelectedProvince([]);
      return;
    }
    if (selectedProvince.includes(value)) {
      setSelectedProvince(selectedProvince.filter((e) => e !== value));
    } else {
      setSelectedProvince([...selectedProvince, value]);
    }
  };

  const handleSchoolTypeFilter = (value) => {
    if (value === "disable") {
      setSelectedSchoolType(schoolTypeValues.map((item) => item.name));
      return;
    }
    if (value === "all") {
      setSelectedSchoolType([]);
      return;
    }
    if (selectedSchoolType.includes(value)) {
      setSelectedSchoolType(selectedSchoolType.filter((e) => e !== value));
    } else {
      setSelectedSchoolType([...selectedSchoolType, value]);
    }
  };

  return (
    <div id="map">
      <Row>
        <Col span={24}>
          <AdvanceFilter
            provinceValues={provinceValues}
            schoolTypeValues={schoolTypeValues}
            handleSchoolTypeFilter={handleSchoolTypeFilter}
            handleProvinceFilter={handleProvinceFilter}
            selectedProvince={selectedProvince}
            selectedSchoolType={selectedSchoolType}
          />
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
