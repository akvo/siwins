import { Store } from "pullstate";

const defaultUIState = {
  advanceSearchValue: [],
  provinceValues: [],
  schoolTypeValues: [],
  indicatorQuestions: [],
  advanceFilterQuestions: [],
  barChartQuestions: [],
  mapData: [],
  schoolTotal: 0,
};

export const UIState = new Store(defaultUIState);
