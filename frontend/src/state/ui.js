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
  provinceFilterValue: {},
};

export const UIState = new Store(defaultUIState);
