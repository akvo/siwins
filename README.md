# SIWINS

[![Build Status](https://akvo.semaphoreci.com/badges/siwins/branches/main.svg?style=shields&key=c2b55481-925e-495b-a4f8-1f0decc20df9)](https://akvo.semaphoreci.com/projects/siwins) [![Repo Size](https://img.shields.io/github/repo-size/akvo/siwins)](https://img.shields.io/github/repo-size/akvo/siwins) [![Coverage Status](https://coveralls.io/repos/github/akvo/siwins/badge.svg?branch=main)](https://coveralls.io/github/akvo/siwins?branch=main) [![Languages](https://img.shields.io/github/languages/count/akvo/siwins)](https://img.shields.io/github/languages/count/akvo/siwins) [![Issues](https://img.shields.io/github/issues/akvo/siwins)](https://img.shields.io/github/issues/akvo/siwins) [![Last Commit](https://img.shields.io/github/last-commit/akvo/siwins/main)](https://img.shields.io/github/last-commit/akvo/siwins/main) [![Documentation Status](https://readthedocs.org/projects/siwins/badge/?version=latest)](https://siwins.readthedocs.io/en/latest/?badge=latest) [![GitHub license](https://img.shields.io/github/license/akvo/siwins.svg)](https://github.com/akvo/siwins/blob/main/LICENSE)

## Development

#### 1. Environment Setup

##### Seed & Sync Auth

This app requires [Akvo Flow API Authentication](https://github.com/akvo/akvo-flow-api/wiki/Authentication) to provides correct credentials when seed or sync form and data points from Akvo FLOW.

Environment Setup:

```
export AUTH0_CLIENT="string"
export AUTH0_USER="string"
export AUTH0_PWD="string"
```

#### 2. Start the App

Now you have all the required environment ready, then run the App using:

```bash
docker-compose up -d
```

To stop:

```bash
docker-compose down
```

Reset the app:

```bash
docker-compose down -v
```

The app should be running at: [localhost:3000](http://localhost:3000). Any endpoints with prefix

- `/api` is redirected to [localhost:5000](http://localhost:5000)
- `/config.js` is a static config that redirected to [localhost:5001/config.js](http://localhost:5000/config.js)

see: [setupProxy.js](https://github.com/akvo/siwins/blob/main/frontend/src/setupProxy.js)

#### 3. Database Seeder

Before you seed the baseline data, please make sure that you have all the required file in the following structure:

Folder Path: **/backend/source/**

```
/backend/source.
└── forms.json
├── charts.js
├── config.min.js
└── bali-topojson.json
```

##### Initial Forms & Data Points seeder

Assuming that you have **forms.json** inside `./backend/source/` folder and have correct [Environment setup](#1-environment-setup) you will be able to run.

```
docker-compose exec backend ./seed.sh
```

##### Sync Data Points

To get updated data points from akvo-flow instance, you need to run:

```
docker-compose exec backend ./sync.sh
```

##### Run Fake Data Points & History seeder

To seed fake data points, run command below:

```
docker-compose exec backend python -m seeder.fake_datapoint <number_of_data_points>
```

To seed fake history for data points, run command below:

```
docker-compose exec backend python -m seeder.fake_history
```

#### Running Test

```bash
docker-compose exec backend ./test.sh
```

---

## Production

```bash
export CI_COMMIT='local'
./ci/build.sh
```

This will generate two docker images with prefix `eu.gcr.io/akvo-lumen/siwins` for backend and frontend

```bash
docker-compose -f docker-compose.yml -f docker-compose.ci.yml up -d
```

Then visit: [localhost:8080](http://localhost:8080). Any endpoints with prefix

- `/api` is redirected to backend API: [localhost:5000](http://localhost:5000)
- `/config.js` is a static config that redirected to [localhost:5001/config.js](http://localhost:5000/config.js)
  inside the network container

see:

- [nginx](https://github.com/akvo/siwins/blob/main/frontend/nginx/conf.d/default.conf) config
- [mainnetwork](https://github.com/akvo/siwins/blob/3047f1b278a974242adec479ec2e11776c473d6d/docker-compose.ci.yml#L49-L54) container setup

### Contact

For further information about the file formats please contact tech.consultancy@akvo.org
