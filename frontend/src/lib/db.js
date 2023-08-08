import Dexie from "dexie";

const dbName = "siwins";
const db = new Dexie(dbName);

db.version(1).stores({
  sync: "++id, cursor",
  sources: "++endpoint, data",
});

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

const getSource = async (endpoint) => {
  const res = await db.sources.get({ endpoint });
  return {
    ...res,
    data: JSON.parse(res.data),
  };
};

const saveSource = ({ endpoint, data }) => {
  return db.sources.put({ endpoint, data: JSON.stringify(data) });
};

const ds = {
  checkDB,
  getSource,
  saveSource,
  truncateSources: () => db.sources.clear(),
  getCursor: async () => await db.sync.get({ id: 1 }),
  saveCursor: ({ cursor }) => db.sync.put({ id: 1, cursor }),
};

export default ds;
