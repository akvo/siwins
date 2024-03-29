import React, { useState, useMemo } from "react";
import { Select, Row, Col, Space, Button, Alert } from "antd";
import {
  CloseCircleFilled,
  CheckCircleFilled,
  InfoCircleOutlined,
} from "@ant-design/icons";
import { isEmpty, sortBy, groupBy } from "lodash";
import { Chart } from "../";

const hints = window.hintjson;
const jmpHints = window.jmphintjson;

const IndicatorDropdown = ({
  loading,
  indicatorQuestion,
  handleOnChangeQuestionDropdown,
  selectedQuestion,
  handleOnChangeQuestionOption,
  selectedOption,
  setValues,
  barChartValues,
}) => {
  const indicatorDropdownOptions = useMemo(() => {
    const grouped = groupBy(indicatorQuestion, "group");
    return Object.keys(grouped).map((key) => {
      const val = grouped[key];
      return {
        key: key.toLowerCase().split(" ").join("-"),
        label: key,
        options: val.map((v) => ({
          label: v?.display_name ? v?.display_name : v.name,
          value: v.id,
        })),
      };
    });
  }, [indicatorQuestion]);

  return (
    <div className="indicator-dropdown-container">
      <Row>
        <Col span={24}>
          <Select
            dropdownMatchSelectWidth={false}
            placement={"bottomLeft"}
            showSearch
            placeholder="Select indicator"
            optionFilterProp="children"
            filterOption={(input, option) =>
              (option?.label ?? "").toLowerCase().includes(input.toLowerCase())
            }
            options={indicatorDropdownOptions}
            onChange={(val) => handleOnChangeQuestionDropdown(val)}
            value={selectedQuestion?.id || []}
            disabled={loading}
          />
          {!isEmpty(selectedQuestion) && (
            <div
              className={`options-container ${selectedQuestion?.type || ""}`}
            >
              <RenderQuestionOption
                loading={loading}
                selectedQuestion={selectedQuestion}
                handleOnChangeQuestionOption={handleOnChangeQuestionOption}
                selectedOption={selectedOption}
                setValues={setValues}
                barChartValues={barChartValues}
              />
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
};

const RenderQuestionOption = ({
  loading,
  selectedQuestion,
  handleOnChangeQuestionOption,
  selectedOption,
  // setValues,
  // barChartValues,
}) => {
  const [showInfo, setShowInfo] = useState(false);
  const [value, setValue] = useState("");

  const MultipleOptionToRender = ({ option }) => {
    return sortBy(option, "order").map((opt) => (
      <Button
        key={`${opt.id}-${opt.name}`}
        style={{
          backgroundColor: selectedOption.includes(opt.name)
            ? "#222"
            : opt.color
            ? opt.color
            : "#1677ff",
        }}
        className={`indicator-dropdown-button ${
          selectedOption.includes(opt.name) ? "selected" : ""
        }`}
        type="primary"
        onClick={() =>
          handleOnChangeQuestionOption(opt.name, selectedQuestion?.type)
        }
        onMouseEnter={() => {
          setValue(opt.name);
          setShowInfo(true);
        }}
        onMouseLeave={() => {
          setValue("");
          setShowInfo(false);
        }}
        disabled={loading}
      >
        <div>
          {selectedOption.includes(opt.name) ? (
            <CloseCircleFilled />
          ) : (
            <CheckCircleFilled />
          )}
          {
            // use option from option-display-name config displayName if defined
            opt?.displayName || opt.name
          }
        </div>
        <InfoCircleOutlined />
      </Button>
    ));
  };

  const NumberOptionToRender = ({ option }) => {
    return (
      <Row>
        <Col className="chart-card" span={24}>
          <Chart
            height={350}
            excelFile={selectedQuestion?.name || "title"}
            type={"LINE"}
            data={option.map((v) => ({
              name: v.value,
              value: v.count,
              count: v.count,
              color: "#70CFAD",
            }))}
            wrapper={false}
            horizontal={false}
            loading={loading}
            // dataZoom={[
            //   {
            //     type: "inside",
            //     realtime: false,
            //     startValue: barChartValues.startValue,
            //     endValue: barChartValues.endValue,
            //     rangeMode: ["value"],
            //   },
            //   {
            //     type: "slider",
            //     realtime: false,
            //     startValue: barChartValues.startValue,
            //     endValue: barChartValues.endValue,
            //     rangeMode: ["value"],
            //   },
            // ]}
            // setValues={setValues}
            grid={{
              top: 70,
              bottom: 60,
              left: 50,
              right: 30,
              show: true,
              containLabel: true,
              label: {
                color: "#222",
              },
            }}
            extra={{
              axisTitle: {
                x: selectedQuestion?.name || "",
                y: "# of Schools",
              },
            }}
            // callbacks={{
            //   onClick: (e) => setValues({ startValue: e, endValue: e }),
            // }}
            showPercent={false}
          />
        </Col>
      </Row>
    );
  };

  if (selectedQuestion.type === "number") {
    return <NumberOptionToRender option={selectedQuestion.number} />;
  }

  const hint = hints.find(
    (f) =>
      f.question_id === selectedQuestion.id && selectedQuestion?.type !== "jmp"
  )?.hint;
  const jmpHint = jmpHints
    .find((f) => f.name === selectedQuestion.name)
    ?.labels?.find((h) => h.name === value)?.hint;

  if (["option", "jmp"].includes(selectedQuestion?.type)) {
    return (
      <Space direction="vertical">
        <MultipleOptionToRender
          option={selectedQuestion.option}
          questionId={selectedQuestion.id}
        />
        {showInfo && (hint || jmpHint) && (
          <div className="option-info-container">
            <Alert message={hint ? hint : jmpHint} type="info" showIcon />
          </div>
        )}
      </Space>
    );
  }
};

export default IndicatorDropdown;
