CREATE USER siwins WITH CREATEDB PASSWORD 'password';

CREATE DATABASE siwins
WITH OWNER = siwins
    TEMPLATE = template0
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';


CREATE DATABASE siwins_test
WITH OWNER = siwins
    TEMPLATE = template0
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';
