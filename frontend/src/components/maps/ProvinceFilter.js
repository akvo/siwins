import React from "react";
import { Space, Dropdown, Button } from "antd";
import { CloseCircleFilled, CheckCircleFilled } from "@ant-design/icons";

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
      <Space direction="horizontal" size="small" style={{ display: "flex" }}>
        <Dropdown
          overlayClassName="bottom-filter"
          dropdownRender={() => (
            <Space
              direction="vertical"
              size="small"
              style={{ display: "flex" }}
            >
              {provinceValues?.map((item) => (
                <Button
                  key={`${item.name}`}
                  type="link"
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
                  onClick={() => handleProvinceFilter(item.name)}
                >
                  {item.name}
                </Button>
              ))}
              <Button
                type="primary"
                onClick={() =>
                  enableProvinanceButton
                    ? handleProvinceFilter("disable")
                    : handleProvinceFilter("all")
                }
                className="enable-button"
                style={{
                  backgroundColor: enableProvinanceButton
                    ? "#dc3545"
                    : "#007bff",
                }}
              >
                {enableProvinanceButton ? "Disable All" : "Enable All"}
              </Button>
            </Space>
          )}
        >
          <Button>Select province</Button>
        </Dropdown>
        <Dropdown
          overlayClassName="bottom-filter"
          dropdownRender={() => (
            <Space
              direction="vertical"
              size="small"
              style={{ display: "flex" }}
            >
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
                  backgroundColor: enableSchoolTypeButton
                    ? "#dc3545"
                    : "#007bff",
                }}
              >
                {enableSchoolTypeButton ? "Disable All" : "Enable All"}
              </Button>
            </Space>
          )}
        >
          <Button>Select school type</Button>
        </Dropdown>
      </Space>
    </div>
  );
};

export default ProvinceFilter;
