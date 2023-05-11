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
      .flatMap((x) =>
        advanceSearchValue[0]?.type === "number" ? x.number : x.option
      )
      .map((x) => encodeURIComponent(x))
      .join(advanceSearchValue[0]?.type === "number" ? "&number=" : "&q=");
    if (advanceSearchValue[0]?.type === "number") {
      url += `${queryUrlPrefix}number=${advanceFilter?.toLowerCase()}`;
    } else {
      url += `${queryUrlPrefix}q=${advanceFilter?.toLowerCase()}`;
    }
    if (advanceSearchValue[0]?.filter === "indicator") {
      url = `${url}&indicator=${advanceSearchValue[0]?.qid}`;
    }
  }
  return url;
};

export const generateFilterURL = (value, url) => {
  if (value?.selectedProvince && value?.selectedProvince.length > 0) {
    const queryUrlPrefix = url.includes("?") ? "&" : "?";
    url = `${url}${queryUrlPrefix}prov=${value?.selectedProvince}`;
  }
  if (value?.selectedSchoolType && value?.selectedSchoolType.length > 0) {
    const queryUrlPrefix = url.includes("?") ? "&" : "?";
    url = `${url}${queryUrlPrefix}sctype=${value?.selectedSchoolType}`;
  }
  return url;
};

export const sequentialPromise = async (promises) => {
  const temp = [];
  for (const promise of promises) {
    const res = await promise;
    temp.push(res.data);
  }
  return temp.flat();
};
