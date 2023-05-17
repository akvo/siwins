import React, { useState, useEffect, useCallback } from "react";
import { Row, Col, List, Space, Button, Tag, Popover } from "antd";
import {
  FileExcelFilled,
  InfoCircleOutlined,
  DownloadOutlined,
} from "@ant-design/icons";
import { api } from "../../lib";
import upperFirst from "lodash/upperFirst";

const ItemDescription = ({ created, tags }) => {
  return (
    <Space direction="vertical">
      <div>{created}</div>
      <div>
        Filters:{" "}
        {tags.length ? (
          tags.map((t, i) => (
            <Tag
              key={i}
              icon={
                <Popover title={upperFirst(t.q)} placement="topRight">
                  <InfoCircleOutlined />
                </Popover>
              }
            >
              {upperFirst(t.o)}
            </Tag>
          ))
        ) : (
          <Tag className="dotted-tag" style={{ margin: 0 }}>
            None
          </Tag>
        )}
      </div>
    </Space>
  );
};

const Export = () => {
  const [fileList, setFileList] = useState([]);
  const [pendingFile, setPendingFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);
  const [page, setPage] = useState(1);
  const [loadMoreButton, setLoadMoreButton] = useState(true);

  useEffect(() => {
    api
      .get("download/list")
      .then((res) => {
        setLoading(false);
        setFileList(res.data);
      })
      .catch(() => {
        setLoading(false);
        setFileList([]);
      });
  }, []);

  const pending = fileList.filter(
    (item) => item.status.toLowerCase() !== "done"
  );

  const checkStatus = useCallback(() => {
    api.get(`download/status?id=${pending?.[0]?.id}`).then((res) => {
      if (res?.data?.status?.toLowerCase() === "done") {
        setPendingFile(res.data);
      }
    });
  }, [pending]);

  useEffect(() => {
    const intervalCall = setInterval(() => {
      if (pending.length && !pendingFile) {
        checkStatus();
      }
    }, 5000);
    return () => {
      clearInterval(intervalCall);
    };
  }, [pendingFile, pending, checkStatus]);

  useEffect(() => {
    if (pendingFile) {
      const currentList = fileList.map((x) => {
        if (pendingFile.id === x.id) {
          return pendingFile;
        }
        return x;
      });
      setFileList(currentList);
      setPendingFile(null);
    }
  }, [pendingFile, fileList]);

  const handleDownload = (payload) => {
    setDownloading(payload);
    api
      .get(`download/file/${payload}`, { responseType: "blob" })
      .then((res) => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", payload);
        document.body.appendChild(link);
        link.click();
        setDownloading(null);
      });
  };

  const onLoadMore = () => {
    api
      .get(`download/list?page=${page + 1}`)
      .then((res) => {
        setFileList([...fileList, ...res.data]);
        setPage(page + 1);
      })
      .catch(() => {
        setLoadMoreButton(false);
      });
  };

  const loadMore =
    !loading && fileList.length > 2 ? (
      <div
        style={{
          textAlign: "center",
          marginTop: 12,
          marginBottom: 12,
          height: 32,
          lineHeight: "32px",
        }}
      >
        {loadMoreButton ? (
          <Button onClick={onLoadMore}>Load More</Button>
        ) : (
          "End of the list"
        )}
      </div>
    ) : null;

  return (
    <div id="dashboard">
      <Row
        className="filter-wrapper main-wrapper"
        align="middle"
        justify="space-between"
      >
        <Col span={24} style={{ padding: "20px 0px" }}>
          <List
            loading={loading}
            bordered={true}
            itemLayout="horizontal"
            loadMore={loadMore}
            dataSource={fileList}
            renderItem={(item) => {
              const filename = item?.payload?.replace("download/", "");
              const done = item?.status?.toLowerCase() === "done";
              const isDownloading = item?.payload === downloading;
              return (
                <List.Item key={item.id}>
                  <List.Item.Meta
                    avatar={
                      <FileExcelFilled
                        style={{
                          marginTop: "7.5px",
                          color: done ? "#52c41a" : "#dddddd",
                          fontSize: "65px",
                        }}
                      />
                    }
                    title={filename}
                    description={
                      <ItemDescription created={item.created} {...item.info} />
                    }
                  />
                  <Button
                    onClick={() => handleDownload(item?.payload)}
                    icon={<DownloadOutlined />}
                    loading={!done || isDownloading}
                    disabled={!done || isDownloading}
                  >
                    {!done
                      ? "Generating"
                      : !isDownloading
                      ? "Download"
                      : "Downloading"}
                  </Button>
                </List.Item>
              );
            }}
          />
        </Col>
      </Row>
    </div>
  );
};

export default Export;
