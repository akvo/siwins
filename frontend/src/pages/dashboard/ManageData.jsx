import React, { useState, useEffect, useCallback } from "react";
import Link from "antd/es/typography/Link";
import AdvanceFilter from "../../components/filter";
import { Row, Col, Table, Breadcrumb } from "antd";
import { UIState } from "../../state/ui";
import { generateAdvanceFilterURL } from "../../util/utils";
import { api } from "../../lib";

const ManageData = () => {
  const { provinceValues, advanceSearchValue, schoolTypeValues } =
    UIState.useState((s) => s);
  const [selectedProvince, setSelectedProvince] = useState([]);
  const [selectedSchoolType, setSelectedSchoolType] = useState([]);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [paginate, setPaginate] = useState({
    total: 1,
    current: 1,
    pageSize: 10,
  });

  const handleProvinceFilter = (value) => {
    setSelectedProvince(value);
  };

  const handleSchoolTypeFilter = (value) => {
    setSelectedSchoolType(value);
  };

  const getdata = useCallback(
    (page = 1, pageSize = 10) => {
      setLoading(true);
      let url = `data?page=${page}&perpage=${pageSize}`;
      url = generateAdvanceFilterURL(advanceSearchValue, url);
      if (selectedProvince && selectedProvince.length > 0) {
        const queryUrlPrefix = url.includes("?") ? "&" : "?";
        url = `${url}${queryUrlPrefix}prov=${selectedProvince}`;
      }
      if (selectedSchoolType && selectedSchoolType.length > 0) {
        const queryUrlPrefix = url.includes("?") ? "&" : "?";
        url = `${url}${queryUrlPrefix}sctype=${selectedSchoolType}`;
      }
      api
        .get(url)
        .then((res) => {
          setData(res.data?.data);
          setPaginate({
            current: res.data.current,
            total: res.data.total,
            pageSize: pageSize,
          });
        })
        .catch(() => {
          setData([]);
        })
        .finally(() => {
          setLoading(false);
        });
    },
    [advanceSearchValue, selectedProvince, selectedSchoolType]
  );

  useEffect(() => {
    getdata();
  }, [getdata]);

  const handleTableChange = (pagination) => {
    const { current, pageSize } = pagination;
    getdata(current, pageSize);
  };

  const columns = [
    {
      title: "School Name",
      dataIndex: "school_information",
      key: "school_name",
      render: (text) => text?.school_name,
    },
    {
      title: "School Type",
      dataIndex: "school_information",
      key: "school_type",
      render: (text) => text?.school_type,
    },
    {
      title: "Provice",
      dataIndex: "school_information",
      key: "province",
      render: (text) => text?.province,
    },
  ];

  return (
    <div id="dashboard">
      <Row className="main-wrapper" align="center">
        <Col span={24}>
          <Row justify="space-between" align="middle">
            <Col span={24}>
              <AdvanceFilter
                prefix={
                  <Col>
                    <Breadcrumb>
                      <Breadcrumb.Item>
                        <Link to="/">Home</Link>
                      </Breadcrumb.Item>
                      <Breadcrumb.Item>
                        <Link to="/dashboard">Dashboard</Link>
                      </Breadcrumb.Item>
                      <Breadcrumb.Item>Manage Data</Breadcrumb.Item>
                    </Breadcrumb>
                  </Col>
                }
                provinceValues={provinceValues}
                schoolTypeValues={schoolTypeValues}
                handleSchoolTypeFilter={handleSchoolTypeFilter}
                handleProvinceFilter={handleProvinceFilter}
                selectedProvince={selectedProvince}
                selectedSchoolType={selectedSchoolType}
              />
            </Col>
          </Row>
        </Col>
        <Col span={24} style={{ padding: "20px 30px" }}>
          <Table
            rowKey={(record) => record.id}
            columns={columns}
            dataSource={data}
            loading={loading}
            onChange={handleTableChange}
            pagination={{
              current: paginate.current,
              total: paginate.total,
            }}
          />
        </Col>
      </Row>
    </div>
  );
};

export default ManageData;
