import React from "react";
import { Space, Button, Collapse } from "antd";
import { CloseCircleFilled, CheckCircleFilled } from "@ant-design/icons";

const { Panel } = Collapse;

const ProvinceFilter = ({
  provinceValues,
  schoolTypeValues,
  handleProvinceFilter,
  handleSchoolTypeFilter,
  selectedProvince,
  selectedSchoolType,
}) => {
  const enableProvinanceButton = selectedProvince.length === 0;
  const enableSchoolTypeButton = selectedSchoolType.length === 0;

  return (
    <div className="bottom-filter-container">
      <Collapse accordion>
        <Panel header="SCHOOL TYPE" key="1">
          <Space direction="vertical" size="small" style={{ display: "flex" }}>
            {schoolTypeValues?.map((item) => (
              <Button
                key={`${item.name}`}
                type="link"
                icon={
                  selectedSchoolType.includes(item.name) ? (
                    <CloseCircleFilled />
                  ) : (
                    <CheckCircleFilled />
                  )
                }
                className={`${
                  selectedSchoolType.includes(item.name) ? "selected" : ""
                }`}
                onClick={() => handleSchoolTypeFilter(item.name)}
              >
                {item.name}
              </Button>
            ))}
            <Button
              type="primary"
              onClick={() =>
                enableSchoolTypeButton
                  ? handleSchoolTypeFilter("disable")
                  : handleSchoolTypeFilter("all")
              }
              className="enable-button"
              style={{
                backgroundColor: enableSchoolTypeButton ? "#dc3545" : "#007bff",
              }}
            >
              {enableSchoolTypeButton ? "Disable All" : "Enable All"}
            </Button>
          </Space>
        </Panel>
        <Panel header="PROVINCE" key="2">
          <Space direction="vertical" size="small" style={{ display: "flex" }}>
            {provinceValues?.map((item) => (
              <Button
                key={`${item.name}`}
                type="link"
                onClick={() => handleProvinceFilter(item.name)}
                icon={
                  selectedProvince.includes(item.name) ? (
                    <CloseCircleFilled />
                  ) : (
                    <CheckCircleFilled />
                  )
                }
                className={`${
                  selectedProvince.includes(item.name) ? "selected" : ""
                }`}
              >
                {item.name}
              </Button>
            ))}
            <Button
              type="primary"
              className="enable-button"
              onClick={() =>
                enableProvinanceButton
                  ? handleProvinceFilter("disable")
                  : handleProvinceFilter("all")
              }
              style={{
                backgroundColor: enableProvinanceButton ? "#dc3545" : "#007bff",
              }}
            >
              {enableProvinanceButton ? "Disable All" : "Enable All"}
            </Button>
          </Space>
        </Panel>
      </Collapse>
    </div>
  );
};

export default ProvinceFilter;
