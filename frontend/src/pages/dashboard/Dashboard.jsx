import { useState } from "react";
import { PieChartOutlined, DesktopOutlined } from "@ant-design/icons";
import { Image, Layout, Menu } from "antd";
const { Header, Content, Sider } = Layout;
import "./style.scss";

function getItem(label, key, icon, children) {
  return {
    key,
    icon,
    children,
    label,
  };
}
const items = [
  getItem("Maps", "1", <PieChartOutlined />),
  getItem("Dashboard", "2", <DesktopOutlined />),
  getItem("Documentation", "3", <DesktopOutlined />),
];
const Dashboard = () => {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <Layout className="dashboard-layout">
      <Sider
        width={300}
        trigger={null}
        collapsed={collapsed}
        onCollapse={(value) => setCollapsed(value)}
      >
        <div className="logo-container">
          <Image src="/images/dashboard-logo.png" preview={false} />
        </div>
        <Menu
          theme="dark"
          defaultSelectedKeys={["1"]}
          mode="inline"
          items={items}
        />
      </Sider>
      <Layout className="site-layout">
        <Header />
        <Content>
          <div>Dashboard</div>
        </Content>
      </Layout>
    </Layout>
  );
};
export default Dashboard;
