import React, { useEffect, useState } from "react";
import {
  Modal,
  Spin,
  Tabs,
  Descriptions,
  Divider,
  Timeline,
  Row,
  Col,
  Switch,
} from "antd";
import { HomeOutlined } from "@ant-design/icons";
import { isEmpty, groupBy, orderBy } from "lodash";
import { api } from "../../lib";
import { Chart } from "..";

const MainTabContent = ({
  id,
  school_information,
  year_conducted,
  jmp_levels,
}) => {
  const keyName = "school-detail-modal-main-";
  // school information
  const School = () => {
    return (
      <>
        <div>{`School: ${school_information?.["school_name"]}(${school_information?.["school_code"]})`}</div>
        <div>{`School Type: ${school_information?.["school_type"]}`}</div>
        <div>{`Province: ${school_information?.["province"]}`}</div>
      </>
    );
  };

  // JMP Level
  const JMPLevel = () => {
    // jmp level
    const groupedJmpLevel = groupBy(jmp_levels, "category");
    return (
      <Descriptions title="JMP Level" layout="vertical">
        {Object.keys(groupedJmpLevel).map((key, i) => {
          const val = orderBy(groupedJmpLevel[key], ["history"]);
          return (
            <Descriptions.Item
              key={`${keyName}-jmp-level-${key}-${i}`}
              label={key}
              labelStyle={{ color: "#000" }}
            >
              <Timeline
                mode="left"
                items={val.map(({ year, level, history, color }) => ({
                  children: (
                    <div>
                      <div>{year}</div>
                      <div>{level}</div>
                    </div>
                  ),
                  color: history ? "gray" : color || "green",
                }))}
              />
            </Descriptions.Item>
          );
        })}
      </Descriptions>
    );
  };

  return (
    <div className="main-tab-content">
      <div className="main-school-information">
        <School />
        <div key={`${keyName}-${id}-year_conducted`}>
          Last updated: {year_conducted}
        </div>
      </div>
      <Divider />
      <div className="main-jmp-level">
        <JMPLevel />
      </div>
    </div>
  );
};

const AnswerTabContent = ({
  dataId,
  question_id,
  question_name,
  render,
  value,
  year,
  history,
}) => {
  const currentChartValues =
    render === "chart"
      ? value.map((v) => ({
          ...v,
          year: year,
          history: history,
          stack: [v],
          value: v.total,
          name: v.level,
        }))
      : [];
  const [chartValues, setChartValues] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (showHistory && isEmpty(chartValues)) {
      setLoading(true);
      const url = `answer/history/${dataId}?question_id=${question_id}`;
      api
        .get(url)
        .then((res) => {
          const { data } = res;
          const transform = data
            .map((d) => {
              return d.value.map((v) => ({
                ...v,
                year: d.year,
                history: d.history,
                stack: [v],
                value: v.total,
                name: v.level,
              }));
            })
            .flat();
          setChartValues(transform);
        })
        .catch((e) => console.error(e))
        .finally(() => {
          setLoading(false);
        });
    }
  }, [showHistory, chartValues, dataId, question_id]);

  const handleOnChangeSwitch = (val) => {
    setShowHistory(val ? question_id : false);
  };

  // render value
  if (render === "value") {
    return (
      <Descriptions title={question_name}>
        <Descriptions.Item>{value}</Descriptions.Item>
      </Descriptions>
    );
  }
  // render chart
  return (
    <Descriptions
      title={
        <Row aligns="middle" justify="space-between">
          <Col span={18} style={{ fontSize: "16px" }}>
            {question_name}
          </Col>
          <Col span={6}>
            <div
              style={{
                float: "right",
                fontWeight: "normal",
                marginRight: "10px",
              }}
            >
              <Switch
                size="small"
                checked={showHistory}
                onChange={handleOnChangeSwitch}
              />{" "}
              Show History
            </div>
          </Col>
        </Row>
      }
    >
      <Descriptions.Item>
        <Chart
          height={350}
          excelFile={"title"}
          type={"BAR"}
          dataZoom={false}
          data={
            showHistory
              ? [...currentChartValues, ...chartValues]
              : currentChartValues
          }
          wrapper={false}
          horizontal={false}
          showPercent={false}
          loading={loading}
          history={showHistory}
          grid={{
            top: 70,
            left: 20,
          }}
        />
      </Descriptions.Item>
    </Descriptions>
  );
};

const SchoolDetailModal = ({ selectedDatapoint, setSelectedDatapoint }) => {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [tabItems, setTabItems] = useState([]);

  useEffect(() => {
    if (!isEmpty(selectedDatapoint)) {
      const { id, school_information } = selectedDatapoint;
      // modal title
      const name = school_information?.school_name;
      const code = school_information?.school_code;
      setTitle(`${name} ${code}`);
      const url = `data/${id}`;
      api
        .get(url)
        .then((res) => {
          const { data } = res;
          // main information
          const main = [
            {
              key: "main",
              label: <HomeOutlined />,
              children: <MainTabContent {...data} />,
            },
          ];
          // group of answer
          const transform = data?.answer.map((a, ai) => {
            return {
              key: `school-detail-tab-${data?.id}-${ai}`,
              label: a.group,
              children: (
                <Row align="middle" justify="space-between" gutter={[8, 8]}>
                  {a.child.map((c, ci) => (
                    <Col
                      span={24}
                      key={`answer-tab-content-${data.id}-${ai}-${ci}`}
                      className="school-description"
                    >
                      <AnswerTabContent dataId={data.id} {...c} />
                      <Divider />
                    </Col>
                  ))}
                </Row>
              ),
            };
          });
          setTabItems([...main, ...transform]);
        })
        .catch((e) => console.error(e))
        .finally(() => setLoading(false));
    }
  }, [selectedDatapoint]);

  return (
    <Modal
      title={title}
      open={!isEmpty(selectedDatapoint)}
      centered
      footer={null}
      width="900px"
      onCancel={() => setSelectedDatapoint({})}
    >
      <div className="school-detail-modal-body">
        {loading ? (
          <div className="loading-wrapper">
            <Spin />
          </div>
        ) : (
          <Tabs items={tabItems} />
        )}
      </div>
    </Modal>
  );
};

export default SchoolDetailModal;
