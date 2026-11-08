\# aSTEP Map Matching!



Matches GPS trajectories from the database to the road network.



\## Before you start



The database lives in the \[data repo](https://github.com/astep-aau/data). Set it up first and wait until `get-data` prints `Done`. After that, just make sure it is running:



```bash

\# in the data repo

docker compose up -d db

```



\## Env stuff



```bash

cp .env.example .env

```



\## Setup



\### Wanna run it?



```bash

docker compose up --build

```



\### Wanna check the database connection?



```bash

docker compose run --rm map-matching repotest

```



\### Wanna run another command?



```bash

docker compose run --rm map-matching <command>

```



\## Something broke?



`password authentication failed for user "postgres"` - you have PostgreSQL installed on your machine using port 5432. Set `POSTGRES\_PORT=5433` in the data repo's `.env`, run `docker compose up -d db` there, and set `DOCKER\_DB\_PORT=5433` in this repo's `.env`.

