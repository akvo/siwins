import React, { useState, useMemo, useEffect } from "react";
import { Row, Col, Card, Switch, Space, Popover } from "antd";
import { Chart } from "../../../components";
import { get } from "lodash";
import { InfoCircleOutlined } from "@ant-design/icons";
import { api, ds } from "../../../lib";
import {
  generateAdvanceFilterURL,
  generateFilterURL,
} from "../../../util/utils";
import { UIState } from "../../../state/ui";

const config = window.dashboardjson?.tabs;
const jmpHints = window.jmphintjson;

const ChartVisual = ({ chartConfig, loading }) => {
  const { title, type, data, provinceValues, index, path, span } = chartConfig;
  const { advanceSearchValue, provinceFilterValue } = UIState.useState(
    (s) => s
  );
  const [isStack, setIsStack] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyLoading, setLoading] = useState(false);
  const [historyData, setHistoryData] = useState([]);

  useEffect(() => {
    let url = `chart/jmp-data/${path}`;
    url = generateAdvanceFilterURL(advanceSearchValue, url);
    url = generateFilterURL(provinceFilterValue, url);
    if (showHistory) {
      setLoading(true);
      (async () => {
        const queryUrlPrefix = url.includes("?") ? "&" : "?";
        url = `${url}${queryUrlPrefix}history=${showHistory}`;
        ds.getDashboard(url)
          .then(async (cachedData) => {
            if (!cachedData) {
              await api.get(url).then((res) => {
                ds.saveDashboard({ endpoint: url, data: res.data });
                setHistoryData(res?.data?.data);
              });
            } else {
              setHistoryData(cachedData.data.data);
            }
          })
          .finally(() => {
            setLoading(false);
          });
      })();
    }
  }, [showHistory, path, setLoading, advanceSearchValue, provinceFilterValue]);

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
          const tempData = showHistory
            ? historyData.concat(r?.data?.data)
            : r?.data?.data;
          let findData = tempData?.filter((d) =>
            showHistory
              ? d.administration === adm.name
              : d.administration === adm.name && !d.history
          );

          // filter findData if not history to remove data from particular year with 0 value
          if (!showHistory) {
            findData = findData
              .map((fd) => {
                const checkValues = fd.child
                  .map((c) => c.count)
                  .filter((x) => x);
                if (!checkValues.length) {
                  return false;
                }
                return fd;
              })
              .filter((x) => x);
          }

          // TODO:: How we want to show the data without history?
          // Disable this merging value for now
          // because we have 2023 and 2018 data as current data
          const disableMergingValue = true;
          if (!showHistory && !disableMergingValue) {
            // Merge child objects into a single array
            const mergedChild = findData.reduce((acc, item) => {
              return acc.concat(item.child);
            }, []);

            // Group merged child objects by option value and sum counts
            const groupedChild = mergedChild.reduce((acc, item) => {
              const key = item.option;
              if (!acc[key]) {
                acc[key] = {
                  ...item,
                  count: 0,
                  percent: 0,
                };
              }
              acc[key].count += item.count;
              return acc;
            }, {});

            // Calculate percent values for each grouped option
            const totalCount = Object.values(groupedChild).reduce(
              (sum, item) => {
                return sum + item.count;
              },
              0
            );

            Object.values(groupedChild).forEach((item) => {
              item.percent = (item.count / totalCount) * 100;
            });

            const findCorrectYear = findData
              .map((item) => {
                const counts = item.child.map((c) => c.count);
                if (counts.every((v) => v === 0)) {
                  return false;
                }
                return item;
              })
              .filter((x) => x)[0];

            const newData = {
              ...findData[0],
              year: findCorrectYear?.year || "",
              child: Object.values(groupedChild),
            };
            findData = [newData];
          }
          // EOL How we want to show the data without history?

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
                count: c.count,
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
          const array = !showHistory ? obj : obj.concat(historyData);
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
                acc.find(({ name, year }) =>
                  showHistory
                    ? name === cur.name && year === cur.year
                    : name === cur.name
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
  }, [data, chartList, isStack, provinceValues, showHistory, historyData]);

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
            excelFile={title}
            type="BARSTACK"
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            extra={{
              axisTitle: {
                y: "Percentage of schools",
              },
            }}
            loading={loading ? loading : historyLoading}
          />
        ) : (
          <Chart
            height={
              chartData.length
                ? 50 *
                    (chartData.find((f) => f.name === path)?.data.length ||
                      10) +
                  188
                : 300
            }
            excelFile={title}
            type={"BAR"}
            showPercent={true}
            dataZoom={false}
            history={showHistory}
            data={chartData.find((f) => f.name === path)?.data}
            wrapper={false}
            horizontal={true}
            extra={{
              axisTitle: {
                y: "Percentage of schools",
              },
            }}
            grid={{
              bottom: "25%",
            }}
            loading={loading ? loading : historyLoading}
          />
        )}
      </Card>
    </Col>
  );
};

export default ChartVisual;
