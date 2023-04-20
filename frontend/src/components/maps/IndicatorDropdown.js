import React from "react";
import { Select, Row, Col, Space, Button, Card } from "antd";
import { CloseCircleFilled, CheckCircleFilled } from "@ant-design/icons";
import isEmpty from "lodash/isEmpty";
import sortBy from "lodash/sortBy";
import { Chart } from "../";

const IndicatorDropdown = ({
  indicatorQuestion,
  handleOnChangeQuestionDropdown,
  selectedQuestion,
  handleOnChangeQuestionOption,
  selectedOption,
  setValues,
  barChartValues,
}) => {
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
            options={indicatorQuestion?.map((q) => ({
              label: q.name,
              value: q.id,
            }))}
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
  const MultipleOptionToRender = ({ option }) => {
    return sortBy(option, "order").map((opt) => (
      <Button
        style={{
          backgroundColor: selectedOption.includes(opt.name)
            ? "#222"
            : "#1677ff",
        }}
        key={`${opt.id}-${opt.name}`}
        type="primary"
        icon={
          selectedOption.includes(opt.name) ? (
            <CloseCircleFilled />
          ) : (
            <CheckCircleFilled />
          )
        }
        onClick={() =>
          handleOnChangeQuestionOption(opt.name, selectedQuestion?.type)
        }
      >
        {opt.name}
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

  if (selectedQuestion?.type === "option") {
    return (
      <Space direction="vertical">
        <MultipleOptionToRender
          option={selectedQuestion.option}
          questionId={selectedQuestion.id}
        />
      </Space>
    );
  }

  return <div>tes</div>;
};

export default IndicatorDropdown;
