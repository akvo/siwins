import React, { useState, useEffect, useCallback } from "react";
import Link from "antd/es/typography/Link";
import AdvanceFilter from "../../components/filter";
import {
  Row,
  Col,
  Table,
  Breadcrumb,
  Select,
  Tabs,
  Spin,
  Button,
  notification,
} from "antd";
import { UIState } from "../../state/ui";
import { generateAdvanceFilterURL } from "../../util/utils";
import { api } from "../../lib";
import { DownloadOutlined } from "@ant-design/icons";

const ManageData = () => {
  const { provinceValues, advanceSearchValue, schoolTypeValues } =
    UIState.useState((s) => s);
  const [selectedProvince, setSelectedProvince] = useState([]);
  const [selectedSchoolType, setSelectedSchoolType] = useState([]);
  const [data, setData] = useState([]);
  const [monitoringData, setMonitoringData] = useState([]);
  const [monitoringRound, setMonitoringRound] = useState("");
  const [loading, setLoading] = useState(false);
  const [tabLoading, setTabLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [paginate, setPaginate] = useState({
    total: 1,
    current: 1,
    pageSize: 10,
  });
  const [tabItems, setTabItems] = useState([]);

  const handleProvinceFilter = (value) => {
    setSelectedProvince(value);
  };

  const handleSchoolTypeFilter = (value) => {
    setSelectedSchoolType(value);
  };

  const handleMonitoringFilter = (value) => {
    setMonitoringRound(value);
  };

  useEffect(() => {
    const url = `option/monitoring_round`;

    api
      .get(url)
      .then((res) => {
        setMonitoringData(res.data);
      })
      .catch(() => {
        setMonitoringData([]);
      });
  }, []);

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
      if (monitoringRound) {
        const queryUrlPrefix = url.includes("?") ? "&" : "?";
        url = `${url}${queryUrlPrefix}monitoring_round=${monitoringRound}`;
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
    [advanceSearchValue, selectedProvince, selectedSchoolType, monitoringRound]
  );

  useEffect(() => {
    getdata();
  }, [getdata]);

  const getSchoolDetails = (id) => {
    setTabLoading(true);
    const url = `answer/data/${id}`;
    api
      .get(url)
      .then((res) => {
        const { data } = res;

        const transform = data?.map((a, ai) => {
          const label = a.group;
          return {
            key: `school-detail-tab-${a?.group}-${ai}`,
            label: label,
            children: <AnswerTabContent title={a.group} data={a.child} />,
          };
        });
        setTabItems([...transform]);
      })
      .catch(() => {
        setTabItems([]);
      })
      .finally(() => {
        setTabLoading(false);
      });
  };

  const handleTableChange = (pagination) => {
    const { current, pageSize } = pagination;
    getdata(current, pageSize);
  };

  const handleExport = () => {
    setExportLoading(true);
    let url = `download/data`;
    url = generateAdvanceFilterURL(advanceSearchValue, url);
    if (selectedProvince && selectedProvince.length > 0) {
      const queryUrlPrefix = url.includes("?") ? "&" : "?";
      url = `${url}${queryUrlPrefix}prov=${selectedProvince}`;
    }
    if (selectedSchoolType && selectedSchoolType.length > 0) {
      const queryUrlPrefix = url.includes("?") ? "&" : "?";
      url = `${url}${queryUrlPrefix}sctype=${selectedSchoolType}`;
    }
    if (monitoringRound) {
      const queryUrlPrefix = url.includes("?") ? "&" : "?";
      url = `${url}${queryUrlPrefix}monitoring_round=${monitoringRound}`;
    }
    api
      .get(url)
      .then(() => {
        notification.success({
          message: "Success",
        });
        setExportLoading(false);
      })
      .catch(() => {
        setExportLoading(false);
      });
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
                suffix={
                  <Button
                    icon={<DownloadOutlined />}
                    onClick={handleExport}
                    disabled={exportLoading}
                  >
                    Export
                  </Button>
                }
                provinceValues={provinceValues}
                schoolTypeValues={schoolTypeValues}
                handleSchoolTypeFilter={handleSchoolTypeFilter}
                handleProvinceFilter={handleProvinceFilter}
                selectedProvince={selectedProvince}
                selectedSchoolType={selectedSchoolType}
              >
                <Select
                  style={{ width: 200 }}
                  allowClear
                  showArrow
                  showSearch
                  placeholder="Select Monitoring Round"
                  optionFilterProp="children"
                  filterOption={(input, option) =>
                    option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0
                  }
                  options={monitoringData.map((x) => ({ label: x, value: x }))}
                  onChange={(val) => handleMonitoringFilter(val)}
                />
              </AdvanceFilter>
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
            expandable={{
              expandIconColumnIndex: columns.length,
              expandedRowRender: () => (
                <>
                  {tabLoading ? (
                    <div className="loading-wrapper">
                      <Spin />
                    </div>
                  ) : (
                    <Tabs items={tabItems} />
                  )}
                </>
              ),
            }}
            onExpand={(expanded, record) => {
              if (expanded) {
                getSchoolDetails(record?.id, record);
              }
            }}
          />
        </Col>
      </Row>
    </div>
  );
};

const AnswerTabContent = ({ title, data }) => {
  const transformData = data.map(({ question_name, type, value }) => ({
    name: question_name,
    type,
    value,
  }));
  const columns = [
    {
      title: "",
      dataIndex: "name",
    },
    {
      title: "",
      dataIndex: "value",
      render: (_, record) => {
        return (
          <>
            {record?.type === "photo" ? (
              <div style={{ height: 200 }}>
                <img src={record.value} />
              </div>
            ) : record?.type === "school_information" ? (
              <div>
                <div>
                  <b>School: </b>
                  {`${record.value?.["school_name"]} (${record.value?.["school_code"]})`}
                </div>
                <div>
                  <b>School Type: </b>
                  {`${record.value?.["school_type"]}`}
                </div>
                <div>
                  <b>Province: </b>
                  {`${record.value?.["province"]}`}
                </div>
              </div>
            ) : (
              record.value
            )}
          </>
        );
      },
    },
  ];
  return (
    <>
      <Table
        className={"answer-table"}
        rowKey={(record) => `${record.name}-${title}`}
        columns={columns}
        dataSource={transformData}
        title={() => title}
        pagination={false}
      />
    </>
  );
};

export default ManageData;