import React, { useEffect, useState, useCallback } from "react";
import {
  Button,
  Space,
  Select,
  Radio,
  Checkbox,
  Tag,
  Popover,
  Row,
  Col,
  Card,
} from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import { UIState } from "../../state/ui";
import isEmpty from "lodash/isEmpty";
import sortBy from "lodash/sortBy";
import { api } from "../../lib";
import { Chart } from "../index";

function AdvanceFilter({ customStyle = {} }) {
  const { advanceSearchValue } = UIState.useState((s) => s);
  const [showAdvanceFilter, setShowAdvanceFilter] = useState(false);
  const [showIndicatorFilter, setShowIndicatorFilter] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState([]);
  const [question, setQuestion] = useState([]);
  const [advancedFilterFeature] = useState({ isMultiSelect: true });

  const handleOnChangeQuestionDropdown = (id) => {
    const filterQuestion = question.find((q) => q.id === id);
    setSelectedQuestion(filterQuestion);
  };

  const getFilterData = useCallback(() => {
    const url = `/question?attribute=advance_filter`;
    api
      .get(url)
      .then((res) => {
        setQuestion(res?.data);
      })
      .catch((e) => console.error(e));
  }, []);

  useEffect(() => {
    getFilterData();
  }, [getFilterData]);

  const handleOnChangeQuestionOption = (value, type) => {
    const filterAdvanceSearchValue = advanceSearchValue.filter(
      (x) => x.qid !== selectedQuestion?.id
    );
    let updatedValue = [
      {
        qid: selectedQuestion?.id,
        question: selectedQuestion?.name,
        option: value,
        type: type,
        filter: showIndicatorFilter ? "indicator" : "advance_filter",
      },
    ];
    if (Array.isArray(value)) {
      updatedValue = value.length ? updatedValue : [];
    }
    UIState.update((s) => {
      s.advanceSearchValue = [...filterAdvanceSearchValue, ...updatedValue];
    });
  };

  return (
    <div>
      <Row className="advance-search-container">
        <Col span={6}>
          <Button
            disabled={showIndicatorFilter}
            onClick={() => {
              setShowIndicatorFilter(false);
              setShowAdvanceFilter(!showAdvanceFilter);
            }}
          >
            Advanced Filter
          </Button>
        </Col>
      </Row>
      {showAdvanceFilter && (
        <div style={customStyle}>
          {/* Question filter */}
          <Space
            direction="vertical"
            className="search-question-option-wrapper"
            size="middle"
            style={{ width: "100%" }}
          >
            {!showIndicatorFilter && (
              <Select
                style={{ width: "100%" }}
                showSearch
                placeholder="Select Question"
                className="search-question-select"
                options={question.map((q) => ({
                  label: q.name,
                  value: q.id,
                }))}
                optionFilterProp="label"
                filterOption={(input, option) =>
                  option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0
                }
                value={!isEmpty(selectedQuestion) ? [selectedQuestion?.id] : []}
                onChange={handleOnChangeQuestionDropdown}
              />
            )}
            {!isEmpty(selectedQuestion) && (
              <>
                <RenderQuestionOption
                  selectedQuestion={selectedQuestion}
                  handleOnChangeQuestionOption={handleOnChangeQuestionOption}
                  advancedFilterFeature={advancedFilterFeature}
                />
                <Button block={true} onClick={() => setSelectedQuestion([])}>
                  Close
                </Button>
              </>
            )}
          </Space>
          {/* Tags of selected filter */}
          {!isEmpty(advanceSearchValue) && <RenderFilterTag />}
        </div>
      )}
    </div>
  );
}

const RenderQuestionOption = ({
  selectedQuestion,
  handleOnChangeQuestionOption,
  advancedFilterFeature,
}) => {
  const { advanceSearchValue } = UIState.useState((s) => s);
  const selectedRadioValue = advanceSearchValue.find(
    (x) => x.qid === selectedQuestion?.id
  );

  const OptionToRender = ({ questionId, option }) => {
    return sortBy(option, "order").map((opt) => (
      <Radio key={`${opt.id}-${opt.name}`} value={`${questionId}|${opt.name}`}>
        {opt.name}
      </Radio>
    ));
  };

  const MultipleOptionToRender = ({ questionId, option }) => {
    return sortBy(option, "order").map((opt) => (
      <Checkbox
        key={`${opt.id}-${opt.name}`}
        value={`${questionId}|${opt.name}`}
      >
        {opt.name}
      </Checkbox>
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
                },
                {
                  type: "slider",
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
            />
          </Card>
        </Col>
      </Row>
    );
  };

  if (selectedQuestion.type === "number") {
    return <NumberOptionToRender option={selectedQuestion.number} />;
  }

  if (
    advancedFilterFeature?.isMultiSelect ||
    selectedQuestion?.type === "multiple_option"
  ) {
    return (
      <Checkbox.Group
        key={`${selectedQuestion.id}-${selectedQuestion.name}`}
        value={selectedRadioValue?.option}
        onChange={(e) =>
          handleOnChangeQuestionOption(e, selectedQuestion?.type)
        }
      >
        <Space direction="vertical">
          <MultipleOptionToRender
            option={selectedQuestion.option}
            questionId={selectedQuestion.id}
          />
        </Space>
      </Checkbox.Group>
    );
  }

  return (
    <Radio.Group
      key={`${selectedQuestion.id}-${selectedQuestion.name}`}
      value={selectedRadioValue?.option}
      onChange={(e) =>
        handleOnChangeQuestionOption(e.target.value, selectedQuestion?.type)
      }
    >
      <Space direction="vertical">
        <OptionToRender
          questionId={selectedQuestion.id}
          option={selectedQuestion.option}
        />
      </Space>
    </Radio.Group>
  );
};

const RenderFilterTag = () => {
  const { advanceSearchValue } = UIState.useState((s) => s);

  const handleOnCloseTag = (type, option) => {
    let deleteFilter = [];
    if (type === "multiselect") {
      deleteFilter = advanceSearchValue
        .map((x) => {
          if (x.option.includes(option)) {
            const filterOpt = x.option.filter((opt) => opt !== option);
            return {
              ...x,
              option: filterOpt.length ? filterOpt : null,
            };
          }
          // other than multiple_options value in advanceSearchValue state
          return x;
        })
        .filter((x) => x.option);
    } else {
      deleteFilter = advanceSearchValue.filter((x) => x.option !== option);
    }
    UIState.update((s) => {
      s.advanceSearchValue = deleteFilter;
    });
  };

  const TagToRender = () => {
    return advanceSearchValue.map((val) => {
      // support multiple select on advanced filter option
      if (Array.isArray(val.option)) {
        return val.option.map((opt) => (
          <Tag
            key={`tag-${opt}`}
            icon={
              <Popover title={val.question} placement="topRight">
                <InfoCircleOutlined />
              </Popover>
            }
            closable
            onClose={() => handleOnCloseTag("multiselect", opt)}
          >
            {opt.split("|")[1]}
          </Tag>
        ));
      }
      return (
        <Tag
          key={`tag-${val.option}`}
          icon={
            <Popover title={val.question} placement="topRight">
              <InfoCircleOutlined />
            </Popover>
          }
          closable
          onClose={() => handleOnCloseTag("radio", val.option)}
        >
          {val.option.split("|")[1]}
        </Tag>
      );
    });
  };

  return (
    <Space size="middle" align="center" wrap>
      <TagToRender />
    </Space>
  );
};

export default AdvanceFilter;
