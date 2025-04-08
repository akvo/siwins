import React, { useState, useEffect } from "react";
import { Image, Layout, Menu, Tooltip } from "antd";
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import "./style.scss";
import { ReactComponent as MapsIcon } from "../../images/icons/maps.svg";
import { ReactComponent as DashboardIcon } from "../../images/icons/dashboard.svg";
import { ReactComponent as DocIcon } from "../../images/icons/db.svg";
import JMPDocIcon from "../../images/icons/jmp-doc.png";
import UserGuideIcon from "../../images/icons/user-guide.png";
import {
  Routes,
  Route,
  useLocation,
  Link,
  useNavigate,
} from "react-router-dom";
import Maps from "./Maps";
import Dashboard from "./Dashboard";
import ManageData from "./ManageData";
import JMPDocumentation from "./JMPDocumentation";
import UserGuide from "./UserGuide";
import { UIState } from "../../state/ui";
import { api, ds, colors } from "../../lib";

const { Content, Sider, Header } = Layout;

const menuItems = [
  { label: "Maps", link: "/dashboard/maps", icon: <MapsIcon />, key: "1" },
  { label: "Dashboard", link: "/dashboard", icon: <DashboardIcon />, key: "2" },
  {
    label: "Database",
    link: "/dashboard/database",
    icon: <DocIcon />,
    key: "3",
  },
  {
    label: "User Guide",
    link: "/dashboard/user-guide",
    icon: <img src={UserGuideIcon} height={30} />,
    key: "4",
  },
  {
    label: "JMP Documentation",
    link: "/dashboard/jmp-documentation",
    icon: <img src={JMPDocIcon} height={35} />,
    key: "5",
  },
];

const dropdownResourceURL = [
  "/question?attribute=indicator",
  "/question?attribute=advance_filter",
  "/question?attribute=generic_bar_chart",
  "/cascade/school_information?level=province",
  "/cascade/school_information?level=school_type",
];

const optionDisplayNameConfig = window?.option_display_name || [];

const remapQuestions = (questions) => {
  return questions.data.map((question) => {
    // remap to option display name
    const findDisplayNameByQuestion = optionDisplayNameConfig.find(
      (x) => x.question_id === question.id
    );
    const remapOptions = question.option.map((opt, opti) => {
      let remapOpt = opt;
      if (findDisplayNameByQuestion?.option) {
        // remap to option display name
        const findOptionDisplayName = findDisplayNameByQuestion.option.find(
          (x) => x.text.toLowerCase() === opt.name.toLowerCase()
        );
        remapOpt = {
          ...remapOpt,
          displayName: findOptionDisplayName?.displayName
            ? findOptionDisplayName.displayName
            : null,
        };
      }
      if (!remapOpt?.color) {
        // remap color
        const colorTemp = colors.option;
        const index = opti % colorTemp.length;
        return {
          ...remapOpt,
          color: colorTemp?.[index],
        };
      }
      return remapOpt;
    });
    return {
      ...question,
      option: remapOptions,
    };
  });
};

const DashboardView = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(true);
  const [fetchFromAPI, setFetchFromAPI] = useState(false);
  const { schoolTotal } = UIState.useState((s) => s);

  useEffect(() => {
    // ** fetch dropdown sources from indexed DB first
    const dsApiCalls = dropdownResourceURL.map((url) => ds.getSource(url));
    Promise.all(dsApiCalls).then((cachedData) => {
      const nullInsideRes = cachedData.filter((x) => !x)?.length;
      if (nullInsideRes) {
        setFetchFromAPI(true);
      } else {
        const [
          indicatorQuestions,
          advanceFilterQuestions,
          generic_bar_chart,
          province,
          school_type,
        ] = cachedData;
        UIState.update((s) => {
          s.indicatorQuestions = indicatorQuestions?.data;
          s.advanceFilterQuestions = advanceFilterQuestions?.data;
          s.barChartQuestions = generic_bar_chart?.data;
          s.provinceValues = province?.data;
          s.schoolTypeValues = school_type?.data;
        });
      }
    });
  }, []);

  useEffect(() => {
    // ** fetch from API if indexed DB not defined
    if (fetchFromAPI) {
      const apiCalls = dropdownResourceURL.map((url) => api.get(url));
      Promise.all(apiCalls).then((res) => {
        const [
          indicatorQuestions,
          advanceFilterQuestions,
          generic_bar_chart,
          province,
          school_type,
        ] = res;
        // remap with custom config
        const remapIndicatorQuestions = {
          ...indicatorQuestions,
          data: remapQuestions(indicatorQuestions),
        };
        const remapAdvanceFilterQuestions = {
          ...advanceFilterQuestions,
          data: remapQuestions(advanceFilterQuestions),
        };
        const remapGenericBarChart = {
          ...generic_bar_chart,
          data: remapQuestions(generic_bar_chart),
        };
        // eol remap with custom config

        // save to indexed DB
        ds.saveSource({
          endpoint: remapIndicatorQuestions.config.url,
          data: remapIndicatorQuestions.data,
        });
        ds.saveSource({
          endpoint: remapAdvanceFilterQuestions.config.url,
          data: remapAdvanceFilterQuestions.data,
        });
        ds.saveSource({
          endpoint: remapGenericBarChart.config.url,
          data: remapGenericBarChart.data,
        });
        ds.saveSource({ endpoint: province.config.url, data: province.data });
        ds.saveSource({
          endpoint: school_type.config.url,
          data: school_type.data,
        });
        // eol save to indexed DB

        UIState.update((s) => {
          s.indicatorQuestions = remapIndicatorQuestions?.data;
          s.advanceFilterQuestions = remapAdvanceFilterQuestions?.data;
          s.barChartQuestions = remapGenericBarChart?.data;
          s.provinceValues = province?.data;
          s.schoolTypeValues = school_type?.data;
        });
        setFetchFromAPI(false);
      });
    }
  }, [fetchFromAPI]);

  const handleOnClickMenu = ({ key }) => {
    const link = menuItems.find((x) => x.key === key)?.link;
    navigate(link);
  };

  return (
    <Layout className="dashboard-layout">
      <Header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 1,
          width: "100%",
        }}
      >
        <div className="logo">
          <Link to="/">
            <Image
              src="/images/dashboard-logo.png"
              preview={false}
              height={40}
            />
          </Link>
          <h4>
            Monitoring WaSH progress for {schoolTotal || 0} schools in Solomon
            Islands{" "}
            <Tooltip title="Number of School Facilities (Based on Unique School Codes) Used for Annual Comparison">
              <span>
                <InfoCircleOutlined style={{ color: "#fff" }} />
              </span>
            </Tooltip>
          </h4>
          <Image src="/images/unicef-logo.png" preview={false} height={20} />
        </div>
      </Header>
      <Layout className="site-layout">
        <Sider trigger={null} collapsible collapsed={collapsed}>
          <div className="logo-container">
            {React.createElement(
              collapsed ? MenuUnfoldOutlined : MenuFoldOutlined,
              {
                className: "trigger",
                onClick: () => setCollapsed(!collapsed),
              }
            )}
          </div>
          <Menu
            defaultSelectedKeys={[
              menuItems.find((item) => item.link === location?.pathname).key,
            ]}
            selectedKeys={
              menuItems.find((item) => item.link === location?.pathname).key
            }
            mode="inline"
            className="menu"
            items={menuItems}
            onClick={handleOnClickMenu}
          />
        </Sider>
        <Content
          className="dashboard-content"
          style={{ marginLeft: collapsed ? 80 : 200 }}
        >
          <Routes>
            <Route exact path="/" element={<Dashboard />} />
            <Route path="/maps" element={<Maps />} />
            <Route path="/database" element={<ManageData />} />
            <Route path="/jmp-documentation" element={<JMPDocumentation />} />
            <Route path="/user-guide" element={<UserGuide />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};
export default DashboardView;
