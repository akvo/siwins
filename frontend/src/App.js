import React from "react";
import "./App.scss";
import { Routes, Route } from "react-router-dom";

import { Layout } from "./components";
import { Home, ErrorPage } from "./pages";

const App = () => {
  return (
    <Layout>
      <Layout.Header />
      <Layout.Body>
        <Routes>
          <Route exact path="/" element={<Home />} />
          <Route exact path="*" element={<ErrorPage status={404} />} />
        </Routes>
      </Layout.Body>
    </Layout>
  );
};

export default App;
