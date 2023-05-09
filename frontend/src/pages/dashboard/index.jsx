import React, { useState, useEffect } from "react";
import { Image, Layout, Menu } from "antd";
import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";
const { Content, Sider, Header } = Layout;
import "./style.scss";
import { ReactComponent as MapsIcon } from "../../images/icons/maps.svg";
import { ReactComponent as DashboardIcon } from "../../images/icons/dashboard.svg";
import { ReactComponent as DocIcon } from "../../images/icons/doc.svg";
import { Routes, Route, useLocation, Link } from "react-router-dom";
import Maps from "./Maps";
import Dashboard from "./Dashboard";
import ManageData from "./ManageData";
import { UIState } from "../../state/ui";
import { api } from "../../lib";

const items = [
  { label: "Maps", link: "/dashboard/maps", icon: <MapsIcon />, key: "1" },
  { label: "Dashboard", link: "/dashboard", icon: <DashboardIcon />, key: "2" },
  {
    label: "Documentation",
    link: "/dashboard/documentation",
    icon: <DocIcon />,
    key: "3",
  },
  {
    label: "Manage Data",
    link: "/dashboard/manage-data",
    icon: <DocIcon />,
    key: "4",
  },
];

const DashboardView = () => {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(true);
  const { schoolTotal } = UIState.useState((s) => s);

  useEffect(() => {
    Promise.all([
      api.get("/question?attribute=indicator"),
      api.get("/question?attribute=advance_filter"),
      api.get("/question?attribute=generic_bar_chart"),
      api.get("/cascade/school_information?level=province"),
      api.get("/cascade/school_information?level=school_type"),
    ]).then((res) => {
      const [
        indicatorQuestions,
        advanceFilterQuestions,
        generic_bar_chart,
        province,
        school_type,
      ] = res;
      UIState.update((s) => {
        s.indicatorQuestions = indicatorQuestions?.data;
        s.advanceFilterQuestions = advanceFilterQuestions?.data;
        s.barChartQuestions = generic_bar_chart?.data;
        s.provinceValues = province?.data;
        s.schoolTypeValues = school_type?.data;
      });
    });
  }, []);

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
              width={40}
            />
          </Link>
          <h3>
            Monitoring WaSH progress for {schoolTotal || 0} schools in Solomon
            Islands
          </h3>
          <Image src="/images/unicef-logo.png" preview={false} height={35} />
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
              items.find((item) => item.link === location.pathname).key,
            ]}
            mode="inline"
            className="menu"
          >
            {items.map((item) => (
              <Menu.Item key={item.key}>
                <div>{item.icon}</div>
                <span>{item.label}</span>
                <Link to={item.link} />
              </Menu.Item>
            ))}
          </Menu>
        </Sider>
        <Content className="dashboard-content">
          <Routes>
            <Route exact path="/" element={<Dashboard />} />
            <Route path="/maps" element={<Maps />} />
            <Route path="/manage-data" element={<ManageData />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};
export default DashboardView;
