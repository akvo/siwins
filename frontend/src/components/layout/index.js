import React from "react";
import Header from "./Header";
import Body from "./Body";
import { Row } from "antd";
import "./style.scss";

const Layout = ({ children, className = "", ...props }) => {
  return <Row className={`${className} layout`}>{children}</Row>;
};

Layout.Header = Header;
Layout.Body = Body;

export default Layout;
