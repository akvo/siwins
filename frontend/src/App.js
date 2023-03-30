import React from "react";
import "./App.scss";
import { Routes, Route, useLocation } from "react-router-dom";

import { Layout } from "./components";
import { Home, Dashboard, ErrorPage } from "./pages";

const App = () => {
  const location = useLocation();
  return (
    <Layout>
      {location.pathname !== "/dashboard" && <Layout.Header />}
      <Layout.Body>
        <Routes>
          <Route exact path="/" element={<Home />} />
          <Route exact path="/dashboard" element={<Dashboard />} />
          <Route exact path="*" element={<ErrorPage status={404} />} />
        </Routes>
      </Layout.Body>
    </Layout>
  );
};

export default App;
