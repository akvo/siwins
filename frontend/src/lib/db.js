import Dexie from "dexie";
import LZString from "lz-string";

const dbName = "siwins";
const db = new Dexie(dbName);

db.version(1).stores({
  sync: "++id, cursor",
  sources: "++endpoint, data", // store resources of dropdown data
  maps: "++endpoint, data", // store data of maps page
  dashboards: "++endpoint, data", // store data of dashboard page
});

const compressData = (data) => LZString.compressToBase64(JSON.stringify(data));
// const compressData = (data) => JSON.stringify(data);
const decompressData = (data) =>
  JSON.parse(LZString.decompressFromBase64(data));
// const decompressData = (data) => JSON.parse(data);

const checkDB = () =>
  Dexie.exists(dbName)
    .then((exists) => {
      if (exists) {
        console.info("Database exists");
      } else {
        console.info("Database doesn't exist");
      }
    })
    .catch((e) => {
      console.error(
        "Oops, an error occurred when trying to check database existance"
      );
      console.error(e);
    });

const getBrowserStorageSize = async () => {
  const res = await navigator.storage.estimate();
  return res;
};

const truncateTables = async () => {
  await db.sources.clear();
  await db.maps.clear();
  await db.dashboards.clear();
};

const getSource = async (endpoint) => {
  const res = await db.sources.get({ endpoint });
  if (!res) {
    return null;
  }
  return {
    ...res,
    data: decompressData(res.data),
  };
};

const saveSource = ({ endpoint, data }) => {
  return db.sources.put({ endpoint, data: compressData(data) });
};

const getMap = async (endpoint) => {
  const res = await db.maps.get({ endpoint });
  if (!res) {
    return null;
  }
  return {
    ...res,
    data: decompressData(res.data),
  };
};

const saveMap = ({ endpoint, data }) => {
  return db.maps.put({ endpoint, data: compressData(data) });
};

const getDashboard = async (endpoint) => {
  const res = await db.dashboards.get({ endpoint });
  if (!res) {
    return null;
  }
  return {
    ...res,
    data: decompressData(res.data),
  };
};

const saveDashboard = ({ endpoint, data }) => {
  return db.dashboards.put({ endpoint, data: compressData(data) });
};

const ds = {
  checkDB,
  getBrowserStorageSize,
  truncateTables,
  getSource,
  saveSource,
  getMap,
  saveMap,
  getDashboard,
  saveDashboard,
  getCursor: async () => await db.sync.get({ id: 1 }),
  saveCursor: ({ cursor }) => db.sync.put({ id: 1, cursor }),
};

export default ds;
