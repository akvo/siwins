import React, { useState } from "react";
import { Row, Col, Select, Breadcrumb } from "antd";
import { Map } from "../../components";
import AdvanceFilter from "../../components/filter";
import { UIState } from "../../state/ui";

function Maps() {
  const [data, setData] = useState([]);
  const [open, setOpen] = useState(false);
  const [value, setValue] = useState();
  const [selectedProvince, setSelectedProvince] = useState([]);
  const [selectedSchoolType, setSelectedSchoolType] = useState([]);
  const { provinceValues, schoolTypeValues, mapData } = UIState.useState(
    (s) => s
  );

  const handleProvinceFilter = (value) => {
    setSelectedProvince(value);
  };

  const handleSchoolTypeFilter = (value) => {
    setSelectedSchoolType(value);
  };

  const handleSearch = (val) => {
    if (val && val.length > 3) {
      setOpen(true);
      const find = mapData
        .filter((item) =>
          item.school_information_array.find((a) =>
            a.toLowerCase().includes(val.toLowerCase())
          )
        )
        ?.map((f) => f.school_information_array);
      setData(find);
    }
  };
  const handleChange = (newValue) => {
    setOpen(false);
    setValue(newValue);
  };

  return (
    <div id="map">
      <Row justify="space-between" align="middle">
        <Col>
          <Breadcrumb>
            <Breadcrumb.Item>Home</Breadcrumb.Item>
            <Breadcrumb.Item>Dashboard</Breadcrumb.Item>
            <Breadcrumb.Item>Maps</Breadcrumb.Item>
          </Breadcrumb>
        </Col>
        <Col>
          <AdvanceFilter
            provinceValues={provinceValues}
            schoolTypeValues={schoolTypeValues}
            handleSchoolTypeFilter={handleSchoolTypeFilter}
            handleProvinceFilter={handleProvinceFilter}
            selectedProvince={selectedProvince}
            selectedSchoolType={selectedSchoolType}
          >
            <Select
              open={open}
              style={{ width: 200 }}
              showSearch
              allowClear
              value={value ? value : null}
              placeholder="Search School"
              defaultActiveFirstOption={false}
              showArrow={false}
              filterOption={false}
              onSearch={handleSearch}
              notFoundContent={null}
              options={(data || []).map((d) => ({
                value: d[2],
                label: d[2],
              }))}
              dropdownMatchSelectWidth={false}
              popupClassName="search-popup"
              onClear={() => setValue("")}
              dropdownRender={() => (
                <>
                  {data.map((item, index) => (
                    <div
                      key={index}
                      className="search-popup-wrapper"
                      onClick={() => handleChange(item[2])}
                    >
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
