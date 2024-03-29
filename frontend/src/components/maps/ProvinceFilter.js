import React from "react";
import { Space, Select } from "antd";

const ProvinceFilter = ({
  provinceValues,
  schoolTypeValues,
  handleProvinceFilter,
  handleSchoolTypeFilter,
  selectedProvince,
  selectedSchoolType,
}) => {
  return (
    <div className="bottom-filter-container">
      <Space direction="horizontal" size="small" style={{ display: "flex" }}>
        <Select
          style={{ width: 200 }}
          dropdownMatchSelectWidth={false}
          placement={"bottomLeft"}
          showSearch
          allowClear
          placeholder="Select province"
          optionFilterProp="children"
          filterOption={(input, option) =>
            (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
          }
          options={provinceValues?.map((q) => ({
            label: q.name,
            value: q.name,
          }))}
          value={selectedProvince}
          onChange={(val) => handleProvinceFilter(val)}
        />
        <Select
          style={{ width: 200 }}
          dropdownMatchSelectWidth={false}
          placement={"bottomLeft"}
          showSearch
          allowClear
          placeholder="Select school type"
          optionFilterProp="children"
          filterOption={(input, option) =>
            (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
          }
          options={schoolTypeValues?.map((q) => ({
            label: q.name,
            value: q.name,
          }))}
          value={selectedSchoolType}
          onChange={(val) => handleSchoolTypeFilter(val)}
        />
      </Space>
    </div>
  );
};

export default ProvinceFilter;
