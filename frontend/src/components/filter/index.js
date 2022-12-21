import React, { useState } from "react";
import { Collapse, Button, Space, Select, Radio } from "antd";
import { FilterOutlined } from "@ant-design/icons";
import { UIState } from "../../state/ui";
import isEmpty from "lodash/isEmpty";
import sortBy from "lodash/sortBy";

const { Panel } = Collapse;

function AdvanceFilter({ customStyle = {} }) {
  const { advanceSearchValue } = UIState.useState((s) => s);
  const [selectedPanel, setSelectedPanel] = useState([]);
  const [selectedQuestion, setSelectedQuestion] = useState([]);
  const [question] = useState([{ id: 1, name: "test" }]);

  const handleOnChangeQuestionDropdown = (id) => {
    const filterQuestion = question.find((q) => q.id === id);
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
      <div className="advance-search-container" style={customStyle}>
        {/* Question filter */}
        <Collapse
          ghost
          collapsible="header"
          className="advance-search-collapse"
          activeKey={selectedPanel}
          onChange={(e) => setSelectedPanel(e)}
        >
          <Panel
            className="advance-search-panel"
            header={<Button icon={<FilterOutlined />}>Advance Filter</Button>}
            showArrow={false}
            key="advance-search"
          >
            <Space
              direction="vertical"
              className="search-question-option-wrapper"
              size="middle"
            >
              <Select
                showSearch
                placeholder="Advance Filter"
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
              {!isEmpty(selectedQuestion) && (
                <>
                  <RenderQuestionOption
                    selectedQuestion={selectedQuestion}
                    handleOnChangeQuestionOption={handleOnChangeQuestionOption}
                  />
                  <Button block={true} onClick={() => setSelectedPanel([])}>
                    Close
                  </Button>
                </>
              )}
            </Space>
          </Panel>
        </Collapse>
      </div>
    </div>
  );
}

const RenderQuestionOption = ({
  selectedQuestion,
  handleOnChangeQuestionOption,
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

export default AdvanceFilter;
