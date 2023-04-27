import { Store } from "pullstate";

const defaultUIState = {
  advanceSearchValue: [],
  provinceValues: [],
  schoolTypeValues: [],
  indicatorQuestions: [],
  advanceFilterQuestions: [],
  barChartQuestions: [],
  mapData: [],
};

export const UIState = new Store(defaultUIState);
