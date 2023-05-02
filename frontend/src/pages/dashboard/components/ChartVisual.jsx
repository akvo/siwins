import React, { useState, useMemo } from "react";
import { Row, Col, Card, Switch, Space } from "antd";
import { Chart } from "../../../components";
import { get } from "lodash";

const config = window.dashboardjson?.tabs;

const ChartVisual = ({ chartConfig }) => {
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

  return (
    <Col key={`col-${type}-${index}`} span={span} className="chart-card">
      <Card>
        <Row className="chart-header" justify="space-between" align="middle">
          <h3>{title}</h3>
          <Space align="center">
            <div>
              <span>Show By Country </span>
              <Switch size="small" checked={isStack} onChange={setIsStack} />
            </div>
            <div>
              <span>History </span>
              <Switch
                size="small"
                checked={showHistory}
                onChange={setShowHistory}
              />
            </div>
          </Space>
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
            loading={!chartData.find((f) => f.name === path)?.data.length}
          />
        ) : (
          <Chart
            height={
              chartData.length
                ? 50 * chartData.find((f) => f.name === path)?.data.length + 188
                : 300
            }
            type={"BAR"}
            dataZoom={false}
            history={true}
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            loading={!chartData.find((f) => f.name === path)?.data.length}
            grid={{
              top: 70,
              left: 120,
            }}
          />
        )}
      </Card>
    </Col>
  );
};

export default ChartVisual;
