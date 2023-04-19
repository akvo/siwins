import React, { useState } from "react";
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
} from "antd";
import { InfoCircleOutlined } from "@ant-design/icons";
import { UIState } from "../../state/ui";
import isEmpty from "lodash/isEmpty";
import sortBy from "lodash/sortBy";

function AdvanceFilter({ customStyle = {} }) {
  const { advanceSearchValue, advanceFilterQuestions } = UIState.useState(
    (s) => s
  );
  const [showAdvanceFilter, setShowAdvanceFilter] = useState(false);
  const [selectedQuestion, setSelectedQuestion] = useState([]);
  const [advancedFilterFeature] = useState({ isMultiSelect: true });

  const handleOnChangeQuestionDropdown = (id) => {
    const filterQuestion = advanceFilterQuestions.find((q) => q.id === id);
    setSelectedQuestion(filterQuestion);
  };

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
        filter: "advance_filter",
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
            onClick={() => {
              setShowAdvanceFilter(!showAdvanceFilter);
            }}
            className={`${showAdvanceFilter ? "selected" : ""}`}
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
            <Select
              style={{ width: "100%" }}
              showSearch
              placeholder="Select Question"
              className="search-question-select"
              options={advanceFilterQuestions?.map((q) => ({
                label: q?.display_name ? q?.display_name : q.name,
                value: q.id,
              }))}
              optionFilterProp="label"
              filterOption={(input, option) =>
                option.label.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
              value={!isEmpty(selectedQuestion) ? [selectedQuestion?.id] : []}
              onChange={handleOnChangeQuestionDropdown}
            />
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
  const selectedRadioValue = advanceSearchValue
    .filter((item) => item.filter === "advance_filter")
    .find((x) => x.qid === selectedQuestion?.id);

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
        .filter((item) => item.filter === "advance_filter")
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
      deleteFilter = advanceSearchValue.filter(
        (x) => x.option !== option && x.filter === "advance_filter"
      );
    }
    UIState.update((s) => {
      s.advanceSearchValue = deleteFilter;
    });
  };

  const TagToRender = () => {
    return advanceSearchValue
      .filter((item) => item.filter === "advance_filter")
      .map((val) => {
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
