import { isEmpty, takeRight } from "lodash";

export const generateAdvanceFilterURL = (advanceSearchValue, url) => {
  // advance search
  if (!isEmpty(advanceSearchValue)) {
    const queryUrlPrefix = url.includes("?") ? "&" : "?";
    advanceSearchValue = advanceSearchValue.map((x) => {
      if (x.type === "answer_list") {
        const option = x.option.map((o) => {
          const oSplit = o.split(" ");
          const qId = o.split("|")[0];
          const oVal = takeRight(oSplit)[0];
          return `${qId}|${oVal}`;
        });
        return { ...x, option };
      }
      return x;
    });
    const advanceFilter = advanceSearchValue
      .flatMap((x) => x.option)
      .map((x) => encodeURIComponent(x))
      .join("&q=");
    url += `${queryUrlPrefix}q=${advanceFilter?.toLowerCase()}`;
    if (advanceSearchValue[0]?.filter === "indicator") {
      url = `${url}&indicator=${advanceSearchValue[0]?.qid}`;
    }
  }
  return url;
};
