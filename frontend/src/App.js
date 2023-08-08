import React, { useEffect } from "react";
import "./App.scss";
import { Routes, Route, useLocation } from "react-router-dom";
import { Layout } from "./components";
import { Home, DashboardView, ErrorPage } from "./pages";
import { UIState } from "./state/ui";
import { api, ds } from "./lib";

const App = () => {
  const location = useLocation();

  useEffect(() => {
    // #TODO:: Fetch cursor here (Replace with correct value)
    ds.saveCursor({ cursor: 456 });
    //
    const url = `chart/number_of_school`;
    // check indexed DB first
    ds.getSource(url).then((cachedData) => {
      if (!cachedData?.endpoint) {
        api
          .get(url)
          .then((res) => {
            ds.saveSource({ endpoint: url, data: res.data });
            UIState.update((s) => {
              s.schoolTotal = res?.data?.total;
            });
          })
          .catch((e) => console.error(e));
      } else {
        UIState.update((s) => {
          s.schoolTotal = cachedData.data.total;
        });
      }
    });
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
