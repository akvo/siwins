import React, { useState } from "react";
import { Row, Col, Select } from "antd";
import { Map } from "../../components";
import AdvanceFilter from "../../components/filter";
import { UIState } from "../../state/ui";

function Maps() {
  const [data, setData] = useState([]);
  const [value, setValue] = useState();
  const [selectedProvince, setSelectedProvince] = useState([]);
  const [selectedSchoolType, setSelectedSchoolType] = useState([]);
  const { provinceValues, schoolTypeValues, mapData } = UIState.useState(
    (s) => s
  );

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

  const handleSearch = (val) => {
    if (val && val.length > 3) {
      const find = mapData
        .filter((item) =>
          item.school_information.find((a) =>
            a.toLowerCase().includes(val.toLowerCase())
          )
        )
        ?.map((f) => f.school_information);
      setData(find);
    }
  };
  const handleChange = (newValue) => {
    setValue(newValue);
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
          >
            <Select
              style={{ width: 200 }}
              showSearch
              value={value}
              placeholder="Search School"
              defaultActiveFirstOption={false}
              showArrow={false}
              filterOption={false}
              onSearch={handleSearch}
              onChange={handleChange}
              notFoundContent={null}
              options={(data || []).map((d) => ({
                value: d[2],
                label: d[2],
              }))}
              dropdownMatchSelectWidth={false}
              popupClassName="search-popup"
              dropdownRender={() => (
                <>
                  {data.map((item, index) => (
                    <div key={index} className="search-popup-wrapper">
                      <h3>{item[2]}</h3>
                      <p>{item[1]}</p>
                    </div>
                  ))}
                </>
              )}
            />
          </AdvanceFilter>
        </Col>
      </Row>
      <Row>
        <Col span={24}>
          <div className="map-wrapper">
            <Map
              selectedProvince={selectedProvince}
              selectedSchoolType={selectedSchoolType}
              searchValue={value}
            />
          </div>
        </Col>
      </Row>
    </div>
  );
}

export default Maps;
