import React, { useEffect, useState } from "react";
import { Modal, Spin, Tabs, Descriptions, Divider, Timeline } from "antd";
import { HomeOutlined } from "@ant-design/icons";
import { isEmpty, capitalize, groupBy, orderBy } from "lodash";
import { api } from "../../lib";

const MainTabContent = ({
  id,
  school_information,
  year_conducted,
  jmp_levels,
}) => {
  const keyName = "school-detail-modal-main-";

  // school information
  const School = () =>
    Object.keys(school_information).map((key) => {
      const name = key
        .split("_")
        .map((x) => capitalize(x))
        .join(" ");
      const val = school_information[key];
      return <div key={`${keyName}-${id}-${key}`}>{`${name}: ${val}`}</div>;
    });

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
          Year Conducted: {year_conducted}
        </div>
      </div>
      <Divider />
      <div className="main-jmp-level">
        <JMPLevel />
      </div>
    </div>
  );
};

const AnswerTabContent = ({ question_id, question_name, render, value }) => {
  // render value
  if (render === "value") {
    return (
      <Descriptions title={question_name}>
        <Descriptions.Item label="Answer">{value}</Descriptions.Item>
      </Descriptions>
    );
  }
  // render chart
  return "Chart";
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
          console.log(data);
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
              children: a.child.map((c, ci) => (
                <div key={`answer-tab-content-${data.id}-${ai}-${ci}`}>
                  <AnswerTabContent {...c} />
                  <Divider />
                </div>
              )),
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
      width="700px"
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
