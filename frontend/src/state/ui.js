import { Store } from "pullstate";

const defaultUIState = {
  advanceSearchValue: [],
  provinceValues: [],
  schoolTypeValues: [],
};

export const UIState = new Store(defaultUIState);
