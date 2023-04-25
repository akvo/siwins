import { Store } from "pullstate";

const defaultUIState = {
  advanceSearchValue: [],
  provinceValues: [],
  schoolTypeValues: [],
  indicatorQuestions: [],
  advanceFilterQuestions: [],
  mapData: [],
};

export const UIState = new Store(defaultUIState);
