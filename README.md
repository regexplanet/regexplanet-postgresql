# regexplanet-postgresql

This is the PostgreSQL backend for RegexPlanet, a tool for online regular expression testing.

See [API docs](http://www.regexplanet.com/support/api.html) for what it is supposed to do.

See [PostgreSQL online regex test page](http://www.regexplanet.com/advanced/postgresql/index.html) to use it to test your regular expressions.


## Running

Run with the environment variable `DATABASE_URL` pointing to a 

## Installation

```sql

CREATE ROLE regex_user LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;

CREATE DATABASE regex
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'en_US.UTF-8'
       LC_CTYPE = 'en_US.UTF-8'
       CONNECTION LIMIT = -1;

GRANT CONNECT, TEMPORARY ON DATABASE regex TO public;
GRANT ALL ON DATABASE regex TO postgres;
GRANT ALL ON DATABASE regex TO regex_user;

ALTER ROLE regex_user PASSWORD 'secret';

CREATE TABLE public.template
(
  id INTEGER NOT NULL,
  target VARCHAR(255),
  CONSTRAINT template_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);

ALTER TABLE public.template OWNER TO regex_user;

```
