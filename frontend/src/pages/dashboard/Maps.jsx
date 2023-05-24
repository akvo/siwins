import React, { useState } from "react";
import { Row, Col, Select, Breadcrumb, notification, Button } from "antd";
import { Map } from "../../components";
import AdvanceFilter from "../../components/filter";
import { UIState } from "../../state/ui";
import { SearchOutlined, DownloadOutlined } from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../lib";

function Maps() {
  const navigate = useNavigate();
  const [data, setData] = useState([]);
  const [open, setOpen] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [value, setValue] = useState();
  const { provinceValues, schoolTypeValues, provinceFilterValue, mapData } =
    UIState.useState((s) => s);

  const handleProvinceFilter = (value) => {
    UIState.update((s) => {
      s.provinceFilterValue = {
        ...s.provinceFilterValue,
        selectedProvince: value,
      };
    });
  };

  const handleSchoolTypeFilter = (value) => {
    UIState.update((s) => {
      s.provinceFilterValue = {
        ...s.provinceFilterValue,
        selectedSchoolType: value,
      };
    });
  };

  const handleExport = () => {
    setExportLoading(true);
    const dataIdsFilter = mapData
      .flatMap((x) => x.id)
      .map((x) => encodeURIComponent(x))
      .join("&data_ids=");
    const url = `download/data?data_ids=${dataIdsFilter}`;
    api
      .get(url)
      .then(() => {
        notification.success({
          message: "Success",
        });
        navigate("/dashboard/database", { state: { isExport: true } });
        setExportLoading(false);
      })
      .catch(() => {
        setExportLoading(false);
      });
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
        <Col span={24}>
          <AdvanceFilter
            provinceValues={provinceValues}
            schoolTypeValues={schoolTypeValues}
            handleSchoolTypeFilter={handleSchoolTypeFilter}
            handleProvinceFilter={handleProvinceFilter}
            selectedProvince={provinceFilterValue?.selectedProvince}
            selectedSchoolType={provinceFilterValue?.selectedSchoolType}
            prefix={
              <Col>
                <Breadcrumb>
                  <Breadcrumb.Item>
                    <Link to="/">Home</Link>
                  </Breadcrumb.Item>
                  <Breadcrumb.Item>
                    <Link to="/dashboard">Dashboard</Link>
                  </Breadcrumb.Item>
                  <Breadcrumb.Item>Maps</Breadcrumb.Item>
                </Breadcrumb>
              </Col>
            }
            suffix={
              <Button
                icon={<DownloadOutlined />}
                onClick={handleExport}
                disabled={exportLoading}
              >
                Export Filtered Data
              </Button>
            }
          >
            <Select
              open={open}
              style={{ width: 200 }}
              showSearch
              allowClear
              value={value ? value : null}
              placeholder="Search School"
              defaultActiveFirstOption={false}
              filterOption={false}
              onSearch={handleSearch}
              notFoundContent={null}
              options={(data || []).map((d) => ({
                value: d[2],
                label: d[2],
              }))}
              suffixIcon={<SearchOutlined />}
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
              selectedProvince={provinceFilterValue?.selectedProvince}
              selectedSchoolType={provinceFilterValue?.selectedSchoolType}
              searchValue={value}
            />
          </div>
        </Col>
      </Row>
    </div>
  );
}

export default Maps;
