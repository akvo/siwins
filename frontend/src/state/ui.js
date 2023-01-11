import { Store } from "pullstate";

const defaultUIState = {
  advanceSearchValue: [],
};

export const UIState = new Store(defaultUIState);
