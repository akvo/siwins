import React from "react";
import { Layout } from "antd";

const Body = ({ children, className = "body", ...props }) => {
  return (
    <Layout className="site-layout">
      <div className={className} {...props}>
        {children}
      </div>
    </Layout>
  );
};

export default Body;
