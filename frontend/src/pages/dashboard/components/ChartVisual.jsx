import React, { useState, useMemo } from "react";
import { Row, Col, Card, Switch, Space } from "antd";
import { Chart } from "../../../components";
import { get } from "lodash";

const config = window.dashboardjson?.tabs;

const ChartVisual = ({ chartConfig, loading }) => {
  const { title, type, data, provinceValues, index, path, span } = chartConfig;
  const [isStack, setIsStack] = useState(false);

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
          const findData = r?.data?.data?.find(
            (d) => d.administration === adm.name
          );
          const stack = findData?.child?.map((c, cx) => {
            return {
              id: cx,
              name: c.option,
              color: c.color,
              order: cx + 1,
              score: 0,
              code: null,
              translations: null,
              value: c.percent,
            };
          });
          return {
            ...adm,
            score: findData?.score,
            stack: stack,
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
          return obj.map((f) => ({
            name: d?.data.question,
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
            data: item.value,
            name: item.name,
          });
        } else {
          found.data = found.data
            .concat([...item.value])
            .reduce((acc, cur, i) => {
              const item = i > 0 && acc.find(({ name }) => name === cur.name);
              if (item) {
                item.count += cur.count;
                item.value += cur.count;
                item.color = cur.color;
              } else {
                acc.push({
                  name: cur.name,
                  count: cur.count,
                  value: cur.count,
                });
              }
              return acc;
            }, []);
        }
      });
      return finalArray;
    }
  }, [data, chartList, isStack, provinceValues]);

  return (
    <Col key={`col-${type}-${index}`} span={span} className="chart-card">
      <Card>
        <Row className="chart-header" justify="space-between" align="middle">
          <h3>{title}</h3>
          <Space align="center">
            <span>Show By County</span>
            <Switch size="small" checked={isStack} onChange={setIsStack} />
          </Space>
        </Row>

        {isStack ? (
          <Chart
            height={
              50 * chartData.find((f) => f.name === path)?.data.length + 188
            }
            type="BARSTACK"
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            loading={loading}
          />
        ) : (
          <Chart
            height={
              50 * chartData.find((f) => f.name === path)?.data.length + 188
            }
            type={"BAR"}
            dataZoom={false}
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            loading={loading}
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
