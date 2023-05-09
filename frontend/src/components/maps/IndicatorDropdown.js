import React, { useState, useMemo } from "react";
import { Select, Row, Col, Space, Button, Card, Alert } from "antd";
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
          />
          {!isEmpty(selectedQuestion) && (
            <div className="options-container">
              <RenderQuestionOption
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
  selectedQuestion,
  handleOnChangeQuestionOption,
  selectedOption,
  setValues,
  barChartValues,
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
        className={`${selectedOption.includes(opt.name) ? "selected" : ""}`}
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
      >
        <div>
          {selectedOption.includes(opt.name) ? (
            <CloseCircleFilled />
          ) : (
            <CheckCircleFilled />
          )}
          {opt.name}
        </div>
        <InfoCircleOutlined />
      </Button>
    ));
  };

  const NumberOptionToRender = ({ option }) => {
    return (
      <Row>
        <Col className="chart-card" span={24}>
          <Card>
            <Chart
              height={350}
              excelFile={"title"}
              type={"BAR"}
              data={option.map((v) => ({
                name: v.value,
                value: v.count,
                count: v.count,
                color: "#70CFAD",
              }))}
              wrapper={false}
              horizontal={false}
              loading={false}
              dataZoom={[
                {
                  type: "inside",
                  realtime: false,
                  start: barChartValues.startValue,
                  end: barChartValues.endValue,
                },
                {
                  type: "slider",
                  realtime: false,
                  start: barChartValues.startValue,
                  end: barChartValues.endValue,
                },
              ]}
              grid={{
                top: 80,
                bottom: 80,
                left: 40,
                right: 20,
                show: true,
                containLabel: true,
                label: {
                  color: "#222",
                },
              }}
              setValues={setValues}
            />
          </Card>
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
