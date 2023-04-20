import { Store } from "pullstate";

const defaultUIState = {
  advanceSearchValue: [],
  provinceValues: [],
  schoolTypeValues: [],
  indicatorQuestions: [],
  advanceFilterQuestions: [],
};

export const UIState = new Store(defaultUIState);
