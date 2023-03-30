import { PieChartOutlined, DesktopOutlined } from "@ant-design/icons";
import { Image, Layout, Menu } from "antd";
const { Header, Content, Sider } = Layout;
import "./style.scss";

const items = [
  { label: "Maps", link: "/dashboard", icon: <PieChartOutlined />, key: "1" },
  { label: "Dashboard", link: "/maps", icon: <DesktopOutlined />, key: "2" },
];

const Dashboard = () => {
  return (
    <Layout className="dashboard-layout">
      <Sider width={300} trigger={null} collapsible>
        <div className="logo-container">
          <Image src="/images/dashboard-logo.png" preview={false} />
        </div>
        <Menu defaultSelectedKeys={["1"]} mode="inline" className="menu">
          {items.map((item) => (
            <Menu.Item key={item.key}>
              <PieChartOutlined />
              <span>{item.label}</span>
            </Menu.Item>
          ))}
        </Menu>
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
