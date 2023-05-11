import React, { useState, useMemo } from "react";
import { Row, Col, Card, Switch, Space, Popover } from "antd";
import { Chart } from "../../../components";
import { get } from "lodash";
import { InfoCircleOutlined } from "@ant-design/icons";

const config = window.dashboardjson?.tabs;
const jmpHints = window.jmphintjson;

const ChartVisual = ({ chartConfig, loading }) => {
  const { title, type, data, provinceValues, index, path, span } = chartConfig;
  const [isStack, setIsStack] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  const chartList = config
    .find((item) => item.component === "JMP-CHARTS")
    ?.chartList.flat();

  const chartData = useMemo(() => {
    if (isStack) {
      const allData = data?.map((r) => {
        const chartSetting = chartList?.find(
          (c) => c.path === r?.data?.question
        );
        const data = provinceValues.map((adm) => {
          const findData = r?.data?.data?.filter((d) =>
            showHistory
              ? d.administration === adm.name
              : d.administration === adm.name && !d.history
          );

          const stack = findData.map((item) => {
            return item?.child?.map((c, cx) => {
              return {
                id: cx,
                name: c.option,
                color: c.color,
                order: cx + 1,
                score: 0,
                code: null,
                translations: null,
                value: c.percent,
                year: item.year,
              };
            });
          });
          return {
            ...adm,
            score: findData?.score,
            stack: stack.flat(),
          };
        });
        return {
          name: r?.data?.question,
          type: chartSetting?.type,
          data: data,
        };
      });
      return allData;
    }
    if (!isStack) {
      const transform = data
        .map((d) => {
          const obj = get(d, "data.data");
          const array = !showHistory ? obj.filter((h) => !h.history) : obj;
          return array.map((f) => ({
            name: d?.data.question,
            year: f.year,
            value: f.child.map((d) => ({
              name: d.option,
              count: d.count,
              percent: d.percent,
              color: d.color,
            })),
          }));
        })
        .filter((x) => x)
        .flatMap((x) => x);

      const finalArray = [];
      transform.map((item) => {
        const found = finalArray.find((ar) => ar.name === item.name);
        if (!found) {
          finalArray.push({
            data: item.value.map((v) => ({ ...v, year: item.year })),
            name: item.name,
            year: item.year,
          });
        } else {
          found.data = found.data
            .concat([...item.value.map((v) => ({ ...v, year: item.year }))])
            .reduce((acc, cur, i) => {
              const item =
                i > 0 &&
                acc.find(
                  ({ name, year }) => name === cur.name && year === cur.year
                );
              if (item) {
                item.count += cur.count;
                item.value += cur.count;
                item.color = cur.color;
              } else {
                acc.push({
                  name: cur.name,
                  count: cur.count,
                  value: cur.count,
                  year: cur.year,
                  color: cur.color,
                });
              }
              return acc;
            }, []);
        }
      });
      return finalArray;
    }
  }, [data, chartList, isStack, provinceValues, showHistory]);

  const content = (path) => {
    const find = jmpHints?.find((item) => item.name === path);
    return (
      <>
        <div className="category">
          <h3>{title}</h3>
          <p>{find?.hint}</p>
        </div>
        <ul>
          {find?.labels.map((item) => (
            <li key={item.name}>
              <h5>
                <span style={{ backgroundColor: item?.color }} />
                {item.name}
              </h5>
              <p>{item.hint}</p>
            </li>
          ))}
        </ul>
      </>
    );
  };

  return (
    <Col key={`col-${type}-${index}`} span={span} className="chart-card">
      <Card>
        <Row className="chart-header" justify="space-between" align="middle">
          <Col span={24}>
            <h3>
              {title}{" "}
              <Popover
                content={content(path)}
                overlayStyle={{
                  width: "30vw",
                }}
                overlayClassName="custom-popover"
              >
                <InfoCircleOutlined />
              </Popover>
            </h3>
          </Col>
          <Col span={24}>
            <Space align="center">
              <div>
                <span>Show By Province </span>
                <Switch size="small" checked={isStack} onChange={setIsStack} />
              </div>
              <div>
                <span>Show History </span>
                <Switch
                  size="small"
                  checked={showHistory}
                  onChange={setShowHistory}
                />
              </div>
            </Space>
          </Col>
        </Row>

        {isStack ? (
          <Chart
            height={
              chartData.length
                ? 50 * chartData.find((f) => f.name === path)?.data.length + 188
                : 200
            }
            type="BARSTACK"
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            loading={loading}
            extra={{
              axisTitle: {
                y: "Percentage of schools",
              },
            }}
          />
        ) : (
          <Chart
            height={
              chartData.length
                ? 50 * chartData.find((f) => f.name === path)?.data.length + 188
                : 300
            }
            type={"BAR"}
            showPercent={true}
            dataZoom={false}
            history={showHistory}
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            loading={loading}
            extra={{
              axisTitle: {
                y: "Percentage of schools",
              },
            }}
            grid={{
              bottom: "25%",
            }}
          />
        )}
      </Card>
    </Col>
  );
};

export default ChartVisual;
