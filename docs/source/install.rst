.. raw:: html

    <style>
      .heading {font-size: 34px; font-weight: 700;}
    </style>

.. role:: heading

:heading:`Getting Started`

Real Time Monitoring Information Systems


Prerequisite
------------

-  Docker > v19
-  Docker Compose > v2.1
-  Docker Sync 0.7.1


Environment Setup
-----------------

Expected that PORT 5432 and 3000 are not being used by other services.

This app requires `Akvo Flow API Authentication <https://github.com/akvo/akvo-flow-api/wiki/Akvo-SSO-login>`__ to provides correct credentials when seed or sync form and data points from Akvo FLOW.

Environment Setup:

.. code:: bash

   export AUTH0_CLIENT="string"
   export AUTH0_USER="string"
   export AUTH0_PWD="string"

Start
^^^^^

For initial run, you need to create a new docker volume.

.. code:: bash

   docker volume create siwins-docker-sync

.. code:: bash

   ./dc.sh up -d

The app should be running at: `localhost:3000 <http://localhost:3000>`__. Any endpoints with prefix - ``^/api/*`` is redirected to `localhost:5000 <http://localhost:5000>`__

Network Config: -
`setupProxy.js <https://github.com/akvo/siwins/blob/main/frontend/src/setupProxy.js>`__
-
`mainnetwork <https://github.com/akvo/siwins/blob/docker-compose.override.yml#L4-L8>`__
container setup

Log
^^^

.. code:: bash

   ./dc.sh log --follow <container_name>

Available containers: - backend - frontend - mainnetwork - db - pgadmin

Stop
^^^^

.. code:: bash

   ./dc.sh down -t 1

Teardown
^^^^^^^^

.. code:: bash

   ./dc.sh down -v
   docker volume rm siwins-docker-sync
