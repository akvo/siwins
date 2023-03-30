import { Image, Layout, Menu } from "antd";
const { Header, Content, Sider } = Layout;
import "./style.scss";
import { ReactComponent as MapsIcon } from "../../images/icons/maps.svg";
import { ReactComponent as DashboardIcon } from "../../images/icons/dashboard.svg";
import { ReactComponent as DocIcon } from "../../images/icons/doc.svg";
import { Routes, Route, useLocation, Link } from "react-router-dom";
import Maps from "./Maps";
import Dashboard from "./Dashboard";

const items = [
  { label: "Maps", link: "/dashboard/maps", icon: <MapsIcon />, key: "1" },
  { label: "Dashboard", link: "/dashboard", icon: <DashboardIcon />, key: "2" },
  {
    label: "Documentation",
    link: "/dashboard/documentation",
    icon: <DocIcon />,
    key: "3",
  },
];

const DashboardView = () => {
  const location = useLocation();

  return (
    <Layout className="dashboard-layout">
      <Sider width={300} trigger={null} collapsible>
        <div className="logo-container">
          <Image src="/images/dashboard-logo.png" preview={false} />
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
      <Layout className="site-layout">
        <Header />
        <Content className="dashboard-content">
          <Routes>
            <Route exact path="/" element={<Dashboard />} />
            <Route path="/maps" element={<Maps />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};
export default DashboardView;
