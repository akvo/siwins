import React, { useEffect } from "react";
import "./App.scss";
import { Routes, Route, useLocation } from "react-router-dom";
import { Layout } from "./components";
import { Home, DashboardView, ErrorPage } from "./pages";
import { UIState } from "./state/ui";
import { api } from "./lib";

const App = () => {
  const location = useLocation();

  useEffect(() => {
    const url = `chart/number_of_school`;
    api
      .get(url)
      .then((res) => {
        UIState.update((s) => {
          s.schoolTotal = res?.data?.total;
        });
      })
      .catch((e) => console.error(e));
  }, []);

  return (
    <Layout>
      {!location.pathname.includes("dashboard") && <Layout.Header />}
      <Layout.Body>
        <Routes>
          <Route exact path="/" element={<Home />} />
          <Route exact path="/dashboard/*" element={<DashboardView />} />
          <Route exact path="*" element={<ErrorPage status={404} />} />
        </Routes>
      </Layout.Body>
    </Layout>
  );
};

export default App;
