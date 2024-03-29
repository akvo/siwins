import React, { useEffect, useState, useMemo } from "react";
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
  Carousel,
  Image,
} from "antd";
import { HomeOutlined, CameraOutlined } from "@ant-design/icons";
import { isEmpty, groupBy, orderBy } from "lodash";
import { api, ds } from "../../lib";
import { Chart } from "..";
import { Resizable } from "react-resizable";

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
        <div>
          <b>School: </b>
          {`${school_information?.["school_name"]} (${school_information?.["school_code"]})`}
        </div>
        <div>
          <b>School Type: </b>
          {`${school_information?.["school_type"]}`}
        </div>
        <div>
          <b>Province: </b>
          {`${school_information?.["province"]}`}
        </div>
      </>
    );
  };

  // JMP Level
  const JMPLevel = () => {
    // jmp level
    const groupedJmpLevelTemp = groupBy(jmp_levels, "category");
    // REORDER jmp level
    const order = ["Water", "Sanitation", "Hygiene"];
    let groupedJmpLevel = {};
    order.forEach((x) => {
      groupedJmpLevel = {
        ...groupedJmpLevel,
        [x]: groupedJmpLevelTemp[x],
      };
    });
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
          <b>Last updated: </b> {year_conducted}
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
  const [chartValues, setChartValues] = useState([]); //history
  const [showHistory, setShowHistory] = useState(false);
  const [loading, setLoading] = useState(false);
  const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);

  const currentChartValues = useMemo(() => {
    if (render !== "chart") {
      return {};
    }
    const res = value.map((v) => {
      return {
        ...v,
        stack: [v],
        year: year,
        history: history,
        name: v.level,
      };
    });
    return res;
  }, [render, value, history, year]);

  const chartData = useMemo(() => {
    if (showHistory) {
      return [...chartValues, ...currentChartValues];
    }
    return currentChartValues;
  }, [showHistory, currentChartValues, chartValues]);

  useEffect(() => {
    if (showHistory && !isHistoryLoaded) {
      setLoading(true);
      const url = `answer/history/${dataId}?question_id=${question_id}`;
      ds.getMap(url).then((cachedData) => {
        if (!cachedData) {
          api
            .get(url)
            .then((res) => {
              const { data } = res;
              const transform = data
                .map((d) => {
                  return d.value.map((v) => {
                    return {
                      ...v,
                      stack: [v],
                      year: d.year,
                      history: d.history,
                      name: v.level,
                    };
                  });
                })
                .flat();
              ds.saveMap({ endpoint: url, data: transform });
              setChartValues(transform);
              setIsHistoryLoaded(true);
            })
            .catch((e) => console.error(e))
            .finally(() => {
              setLoading(false);
            });
        } else {
          setChartValues(cachedData.data);
          setIsHistoryLoaded(true);
          setLoading(false);
        }
      });
    }
  }, [showHistory, isHistoryLoaded, dataId, question_id]);

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
          excelFile={question_name}
          type={"BAR"}
          dataZoom={false}
          data={chartData}
          wrapper={false}
          horizontal={false}
          showPercent={false}
          loading={loading}
          history={showHistory}
          reduceHistoryValue={false}
          grid={{
            top: 70,
            left: 20,
          }}
        />
      </Descriptions.Item>
    </Descriptions>
  );
};

const ImageContent = ({ child }) => {
  return (
    <Carousel autoplay dotPosition="bottom" effect="fade">
      {child.map((c) => {
        return (
          <div
            key={`answer-tab-content-image-${c.question_id}`}
            style={{
              margin: 0,
              width: "100%",
              position: "relative",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                background: "#000",
                opacity: 0.55,
                width: "100%",
                position: "absolute",
                top: 0,
                padding: 8,
                color: "#fff",
                zIndex: 1,
              }}
            >
              {c.question_name}
            </div>
            <Image
              width="100%"
              height={410}
              style={{ objectFit: "cover" }}
              src={c.value}
              alt={c.question_name}
            />
          </div>
        );
      })}
    </Carousel>
  );
};

const SchoolDetailModal = ({ selectedDatapoint, setSelectedDatapoint }) => {
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [tabItems, setTabItems] = useState([]);

  const defModalSize = { width: 900, height: 575 };
  const windowSize = {
    width: window.innerWidth - 100,
    height: window.innerHeight - 100,
  };
  const [modalSize, setModalSize] = useState(defModalSize);

  useEffect(() => {
    if (!isEmpty(selectedDatapoint)) {
      const { id, school_information } = selectedDatapoint;
      // modal title
      const name = school_information?.school_name;
      const code = school_information?.school_code;
      setTitle(`${name} (${code})`);
      const url = `data/${id}`;
      ds.getMap(url).then((cachedData) => {
        if (!cachedData) {
          api
            .get(url)
            .then((res) => {
              ds.saveMap({ endpoint: url, data: res.data });
              setTabItems(res.data);
            })
            .catch((e) => console.error(e))
            .finally(() => setLoading(false));
        } else {
          setTabItems(cachedData.data);
          setLoading(false);
        }
      });
    }
  }, [selectedDatapoint]);

  const handleOnCancelModal = () => {
    setModalSize(defModalSize);
    setSelectedDatapoint({});
  };

  const handleOnResize = (event, { size }) => {
    if (!event.isTrusted) {
      return;
    }
    const { width, height } = size;
    const { width: defWidth, height: defHeight } = defModalSize;
    const { width: windowWidth, height: windowHeight } = windowSize;

    let newWidth = width;
    if (width <= defWidth) {
      newWidth = defWidth;
    }
    if (width >= windowWidth) {
      newWidth = windowWidth;
    }

    let newHeight = height;
    if (height <= defHeight) {
      newHeight = defHeight;
    }
    if (height >= windowHeight) {
      newHeight = windowHeight;
    }
    setModalSize({ width: newWidth, height: newHeight });
  };

  const tabItemComponent = useMemo(() => {
    if (isEmpty(tabItems)) {
      return [];
    }
    const data = tabItems;
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
      const isImage = a.group.toLowerCase() === "images";
      const label = isImage ? <CameraOutlined /> : a.group;
      if (isImage) {
        return {
          key: `school-detail-tab-${data?.id}-${ai}`,
          label: label,
          children: <ImageContent {...a} />,
        };
      }
      return {
        key: `school-detail-tab-${data?.id}-${ai}`,
        label: label,
        children: (
          <Row
            align="middle"
            justify="space-between"
            gutter={[8, 8]}
            style={{
              height: `${modalSize.height - 125}px`,
              width: `${modalSize.width - 55}px`,
            }}
          >
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
    return [...main, ...transform];
  }, [tabItems, modalSize]);

  return (
    <Modal
      title={title}
      open={!isEmpty(selectedDatapoint)}
      centered
      footer={null}
      mask={false}
      width="min-content"
      style={{ pointerEvents: "all" }}
      wrapProps={{ style: { pointerEvents: "none" } }}
      onCancel={handleOnCancelModal}
      destroyOnClose={true}
    >
      <Resizable
        width={modalSize.width}
        height={modalSize.height}
        onResize={handleOnResize}
      >
        <div
          className="school-detail-modal-body"
          style={{
            height: `${modalSize.height}px`,
            width: `${modalSize.width}px`,
          }}
        >
          {loading ? (
            <div className="loading-wrapper">
              <Spin />
            </div>
          ) : (
            <Tabs items={tabItemComponent} />
          )}
        </div>
      </Resizable>
    </Modal>
  );
};

export default SchoolDetailModal;
