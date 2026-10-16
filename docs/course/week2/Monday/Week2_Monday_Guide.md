# Week 2, Monday: Design and Start the Patent Database

AI Patent Intelligence Platform for III-V Semiconductor Lasers. Follow the steps in order, on Windows with PowerShell. Week 2 turns the one-off download into a repeatable pipeline that loads clean data into PostgreSQL. Today builds the database it will load into.

## Today at a glance

1. Install Docker Desktop and check that it runs.
2. Add the database settings to `.env` (the password stays there) and create `.env.example`.
3. Install `psycopg2-binary`.
4. Create `docker-compose.yml` and start PostgreSQL.
5. Learn the schema design and write `docs/schema.md`.
6. Create the tables with `sql/01_schema.sql`.
7. Load the Week 1 data with `src/load_week1_to_db.py`.
8. Run 10 practice SQL queries (`sql/02_practice_queries.sql`).
9. Commit and push to GitHub.

**Result:** a running database with 2,248 patents, a documented schema and a pushed repository.

## Before you start

**What you will have at the end:** PostgreSQL running in Docker, seven tables filled with the Week 1 data, `docs/schema.md`, and 10 queries you ran yourself.

**Time needed:** about 3 to 4 hours (the Docker install is the slow part). **Week 2 goal:** a repeatable pipeline into PostgreSQL. Monday builds the database, Thursday the collector, Friday the cleaning and the final load.

**What you need from Week 1:** `data/processed/patents_tagged.csv` (2,248 rows), the `(.venv)` environment and `.env` with the EPO key and secret.

**How to read each step:** Why is the reason. Do this is what to type or click. It worked if is your check. If it goes wrong lists the usual problems and the fix. Run commands from the project root, with `(.venv)` showing in the prompt.

**Passwords:** never write the database password in chat, in code or on GitHub. It lives only in `.env`, which `.gitignore` already blocks.

## Decisions made today

| Decision | Choice | Reason |
|---|---|---|
| Where PostgreSQL runs | In Docker, not installed on Windows | One command starts it, and anyone can copy the setup. |
| Rows in `patents` | One per patent document, with a `family_id` column | Matches what we download. Families are counted with `COUNT(DISTINCT family_id)`. |
| Lists (companies, inventors, codes) | Own table plus a link table each | A patent has many of each, and a company has many patents. |
| Company names | Stored raw, `name_clean` left empty | Merging variants is Friday's task. The raw data is never lost. |
| Tags | Kept as columns in `patents` for now | Quick queries on Week 1 results. They can move later. |
| Loader today | Empties the tables, then loads | Simple and repeatable. The update-aware loader comes on Friday. |

## Words you will see

| Word | Meaning |
|---|---|
| PostgreSQL | A database program that stores data in tables and answers SQL questions. |
| Docker | A tool that runs programs in isolated boxes called containers. |
| Container | One running box. Ours holds PostgreSQL. |
| Image | The recipe a container starts from (`postgres:16`). |
| Volume | A storage area Docker keeps, so the data survives restarts. |
| Schema | The design: which tables exist and how they connect. |
| Table, row, column | A table is a sheet. Each row is one record, each column one field. |
| Primary key | A column whose value is different in every row, such as `patent_id`. |
| Foreign key | A column that points to a row in another table. |
| Link table | A table that only stores pairs, such as patent 5 and company 12. |
| SQL | The language used to ask a database questions. |
| `psql` | The text program inside the container to type SQL. |

## Step 1: Install Docker Desktop

**Why:** Docker lets us start PostgreSQL with one file and one command, with no manual database install.

**You need:** Windows 10 or 11 and an internet connection.

**Do this:** download Docker Desktop for Windows from docker.com, run the installer with the default options (WSL 2), restart the computer if it asks, and open Docker Desktop. Wait until it says it is running. Then in PowerShell:

```powershell
docker --version
docker compose version
```

**It worked if:** both commands print a version number, and Docker Desktop shows as running.

**If it goes wrong**

- `docker` is not recognized. Fix: close and reopen PowerShell and VS Code, or restart Windows after the install.
- `error during connect` or `dockerDesktopLinuxEngine`. Fix: Docker Desktop is not started. Open it and wait for it to say running.
- It asks for WSL or virtualization. Fix: run `wsl --update` in PowerShell, restart, and make sure virtualization is on in the BIOS if it still complains.

## Step 2: Add the database settings to `.env`

**Why:** Docker reads the database name, user and password from `.env`, so the password is never written in a file that goes to GitHub.

**You need:** your existing `.env` with the EPO lines.

**Do this:** open `.env` and add these lines. Choose your own password with letters and numbers only (symbols such as `#` and `$` confuse the file).

```text
POSTGRES_USER=patents
POSTGRES_DB=patents
POSTGRES_PASSWORD=choose-your-own-password-here
POSTGRES_PORT=5432
```

Then create a second file, `.env.example`, with the same lines but a fake password. This one is safe to commit. It shows other people which settings the project needs.

```text
EPO_CONSUMER_KEY=your-key-here
EPO_CONSUMER_SECRET=your-secret-here
POSTGRES_USER=patents
POSTGRES_DB=patents
POSTGRES_PASSWORD=your-password-here
POSTGRES_PORT=5432
```

**It worked if:** `.env` has the four new lines and `git status` does not list `.env` (it is ignored). `.env.example` does appear.

**If it goes wrong**

- `.env` shows in `git status`. Fix: check `.gitignore` contains the line `.env`, then run `git rm --cached .env` if it was ever added.
- The file is saved as `.env.txt`. Fix: rename it. In VS Code, turn on "show file extensions" or use Rename in the Explorer.

## Step 3: Install the Python libraries

**Why:** Python needs `psycopg2-binary` to talk to PostgreSQL. `python-dotenv` (already installed) reads `.env`.

**You need:** the `(.venv)` prompt.

**Do this**

```powershell
pip install psycopg2-binary
pip freeze > requirements.txt
```

**It worked if:** `pip` ends with "Successfully installed psycopg2-binary" and `requirements.txt` now contains a `psycopg2-binary` line.

**If it goes wrong**

- `pip` is not recognized. Fix: the environment is not active. Run `.venv\Scripts\Activate.ps1`.
- A build error mentioning `pg_config`. Fix: you installed `psycopg2` and not `psycopg2-binary`. Install the `-binary` one.

## Step 4: Create `docker-compose.yml` and start PostgreSQL

**Why:** this file describes the database container. Anyone with Docker can start the same database from it.

**You need:** Steps 1 and 2 done and Docker Desktop running.

**Do this:** create `docker-compose.yml` in the project root (next to `.env`) and create an empty folder `sql` next to it. Docker will show our `sql` files inside the container.

```yaml
services:
  db:
    image: postgres:16
    container_name: patents_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./sql:/sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
```

How to read it: `image` is the PostgreSQL version. The three `environment` lines take their values from `.env`. `ports` connects port 5432 of your computer to the container. `volumes` keeps the data in `pgdata` and shows `./sql` inside the container as `/sql`. `healthcheck` lets Docker test that the database is ready.

Start it:

```powershell
docker compose up -d
docker compose ps
```

**It worked if:** `docker compose ps` shows `patents_db` with status `running` or `healthy`. The first start downloads the image, which takes a minute.

**If it goes wrong**

- `variable is not set` warnings. Fix: a name in `.env` is misspelled. It must be exactly `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`.
- `port is already allocated`. Fix: another program uses 5432. Change `POSTGRES_PORT=5433` in `.env` and run `docker compose up -d` again.
- The container keeps restarting. Fix: look at `docker compose logs db` for the reason. A missing `POSTGRES_PASSWORD` is the usual cause.
- Later, `password authentication failed`. Fix: the volume remembers the first password. If you changed it afterwards, run `docker compose down -v` (this deletes the data) and `docker compose up -d`.

## Step 5: Learn the schema and write `docs/schema.md`

**Why:** the design decides how easy every later question is. A patent has several companies, several inventors and several CPC codes, and one company has many patents. Putting them in one wide table would repeat data and break counting. So each list gets its own table, joined by a link table.

**You need:** nothing installed. This step is thinking and writing.

**The picture:** `patents` is in the centre. Three link tables connect it to `assignees` (companies), `inventors` and `cpc_codes`. A row in a link table says "this patent has this company". The `position` column keeps the order, so position 1 is the lead applicant.

**Do this:** create the folder `docs` if needed and save this as `docs/schema.md`. It is the deliverable for today.

```markdown
# Database schema

PostgreSQL 16, database `patents`. Created by `sql/01_schema.sql`.

## Tables

patents: one row per published patent document (for example EP3456789A1)
- patent_id (primary key), publication_number (unique), family_id
- publication_date, application_date, priority_date, priority_year
- title, abstract, abstract_lang, cited_count
- material, emission, application, noise_flag (Week 1 tags)

assignees: one row per company name
- assignee_id (primary key), name_raw (unique, as EPO gives it)
- name_clean (empty until Week 2 Friday)

inventors: one row per person
- inventor_id (primary key), name (unique)

cpc_codes: one row per classification code
- cpc_id (primary key), code (unique, for example H01S5/343)

## Link tables (many-to-many)

patent_assignees: patent_id, assignee_id, position (1 = lead applicant)
patent_inventors: patent_id, inventor_id, position
patent_cpc: patent_id, cpc_id

## How the tables connect

patents 1 --- many patent_assignees many --- 1 assignees
patents 1 --- many patent_inventors many --- 1 inventors
patents 1 --- many patent_cpc       many --- 1 cpc_codes

## Design decisions

- One patent can have several companies, inventors and codes, and one company has many
  patents. A link table stores each pair once. That is why each list has its own table.
- A family is not a table yet. Patents of one family share a family_id, and queries
  count DISTINCT family_id.
- Names are stored exactly as received. Merging variants (Sony Corp, Sony Group Corp)
  happens on Friday in name_clean, so the raw data is never lost.
- Deleting a patent also deletes its link rows (ON DELETE CASCADE).

## Not stored yet

Cited patents, claims text and embeddings (Week 3).
```

**It worked if:** you can explain in one sentence why `patent_assignees` exists.

**If it goes wrong**

- You are unsure why a link table is needed. Fix: imagine a company column on `patents` with "Sony; Sony Group" in it. You could not count patents per company with a simple query. Rows in a link table can be counted.

## Step 6: Create the tables

**Why:** the design only exists on paper until the tables are created in the database.

**You need:** the container running (Step 4).

**Do this:** create `sql/01_schema.sql` with this content.

```sql
-- Schema for the AI Patent Intelligence Platform (Week 2, Monday).
-- Safe to run again: it drops and recreates the tables.

DROP TABLE IF EXISTS patent_cpc, patent_inventors, patent_assignees CASCADE;
DROP TABLE IF EXISTS cpc_codes, inventors, assignees, patents CASCADE;

-- One row per published patent document (for example EP3456789A1).
CREATE TABLE patents (
    patent_id          SERIAL PRIMARY KEY,
    publication_number TEXT NOT NULL UNIQUE,
    family_id          TEXT,
    publication_date   DATE,
    application_date   DATE,
    priority_date      DATE,
    priority_year      INTEGER,
    title              TEXT,
    abstract           TEXT,
    abstract_lang      TEXT,
    cited_count        INTEGER DEFAULT 0,
    -- Tags from the Week 1 tagging (kept here for now, refined in later weeks)
    material           TEXT,
    emission           TEXT,
    application        TEXT,
    noise_flag         BOOLEAN DEFAULT FALSE
);

-- One row per company name. name_raw is exactly as EPO gives it.
-- name_clean stays empty until Week 2 Friday, when the variants of one company are merged.
CREATE TABLE assignees (
    assignee_id SERIAL PRIMARY KEY,
    name_raw    TEXT NOT NULL UNIQUE,
    name_clean  TEXT
);

CREATE TABLE inventors (
    inventor_id SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE
);

CREATE TABLE cpc_codes (
    cpc_id SERIAL PRIMARY KEY,
    code   TEXT NOT NULL UNIQUE
);

-- Link tables: one row for each "this patent has this company / person / code".
-- position 1 is the first name listed on the patent (the lead applicant).
CREATE TABLE patent_assignees (
    patent_id   INTEGER NOT NULL REFERENCES patents(patent_id) ON DELETE CASCADE,
    assignee_id INTEGER NOT NULL REFERENCES assignees(assignee_id),
    position    INTEGER NOT NULL,
    PRIMARY KEY (patent_id, assignee_id)
);

CREATE TABLE patent_inventors (
    patent_id   INTEGER NOT NULL REFERENCES patents(patent_id) ON DELETE CASCADE,
    inventor_id INTEGER NOT NULL REFERENCES inventors(inventor_id),
    position    INTEGER NOT NULL,
    PRIMARY KEY (patent_id, inventor_id)
);

CREATE TABLE patent_cpc (
    patent_id INTEGER NOT NULL REFERENCES patents(patent_id) ON DELETE CASCADE,
    cpc_id    INTEGER NOT NULL REFERENCES cpc_codes(cpc_id),
    PRIMARY KEY (patent_id, cpc_id)
);

-- Indexes for the joins and filters we use most
CREATE INDEX idx_patents_family   ON patents(family_id);
CREATE INDEX idx_patents_priority ON patents(priority_year);
CREATE INDEX idx_pa_assignee      ON patent_assignees(assignee_id);
CREATE INDEX idx_pi_inventor      ON patent_inventors(inventor_id);
CREATE INDEX idx_pc_cpc           ON patent_cpc(cpc_id);
```

Run it inside the container (the user and database names match your `.env`):

```powershell
docker compose exec db psql -U patents -d patents -f /sql/01_schema.sql
docker compose exec db psql -U patents -d patents -c "\dt"
```

**It worked if:** the second command lists seven tables: `assignees`, `cpc_codes`, `inventors`, `patent_assignees`, `patent_cpc`, `patent_inventors` and `patents`.

**If it goes wrong**

- `No such file` for `/sql/01_schema.sql`. Fix: the `sql` folder must be in the same folder as `docker-compose.yml`. Run `docker compose down` and `docker compose up -d` after you create it.
- `role "patents" does not exist`. Fix: the user in `.env` is not `patents`, or the volume was created with another name. Use your own user name in the command, or run `docker compose down -v` and start again.
- `database "patents" does not exist`. Fix: same reason. Use your `POSTGRES_DB` value in `-d`.

## Step 7: Load the Week 1 data

**Why:** a database without data cannot be practised on. This script reads the tagged CSV, converts the dates and numbers, and fills the seven tables.

**You need:** Steps 3 and 6 done, and `data/processed/patents_tagged.csv` from Friday.

**Do this:** create `src/load_week1_to_db.py` and run it.

```python
"""Week 2, Monday: load the Week 1 tagged patents into PostgreSQL.

Reads  data/processed/patents_tagged.csv
Writes the tables patents, assignees, inventors, cpc_codes and the three link tables.

Run from the project root:  python src/load_week1_to_db.py
Safe to run again: it empties the tables first. (The final loader with updates comes on Friday.)
"""
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import find_dotenv, load_dotenv
from psycopg2.extras import execute_values

INPUT = Path("data/processed/patents_tagged.csv")


def connect():
    """Connect with the settings from .env. The password is never written in the code."""
    load_dotenv(find_dotenv(usecwd=True))
    return psycopg2.connect(
        host="localhost",
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def to_date(value):
    """'20200131' becomes a date, an empty text becomes None (NULL in the database)."""
    parsed = pd.to_datetime(value, format="%Y%m%d", errors="coerce")
    return None if pd.isna(parsed) else parsed.date()


def to_int(value):
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else int(number)


def split_list(value):
    """'A; B; A' becomes ['A', 'B'] : no empty items, no repeats, order kept."""
    items = []
    for item in str(value).split(";"):
        item = item.strip()
        if item and item not in items:
            items.append(item)
    return items


def main():
    df = pd.read_csv(INPUT, dtype=str, keep_default_na=False)
    print(f"Read {len(df)} rows from {INPUT}")

    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "TRUNCATE patent_cpc, patent_inventors, patent_assignees, "
        "cpc_codes, inventors, assignees, patents RESTART IDENTITY CASCADE"
    )

    # 1. patents
    rows = [
        (
            r.number, r.family_id or None, to_date(r.publication_date), to_date(r.application_date),
            to_date(r.priority_date), to_int(r.priority_year), r.title, r.abstract, r.abstract_lang or None,
            to_int(r.cited_count) or 0, r.material, r.emission, r.application, r.noise_flag == "True",
        )
        for r in df.itertuples()
    ]
    execute_values(
        cur,
        "INSERT INTO patents (publication_number, family_id, publication_date, application_date, "
        "priority_date, priority_year, title, abstract, abstract_lang, cited_count, material, emission, "
        "application, noise_flag) VALUES %s",
        rows,
    )
    cur.execute("SELECT publication_number, patent_id FROM patents")
    patent_id = dict(cur.fetchall())

    # 2. names and codes, then the link tables
    for column, table, name_col, id_col, link, has_position in [
        ("applicants", "assignees", "name_raw", "assignee_id", "patent_assignees", True),
        ("inventors", "inventors", "name", "inventor_id", "patent_inventors", True),
        ("cpc", "cpc_codes", "code", "cpc_id", "patent_cpc", False),
    ]:
        per_patent = {r.number: split_list(getattr(r, column)) for r in df.itertuples()}
        unique = sorted({item for items in per_patent.values() for item in items})
        execute_values(cur, f"INSERT INTO {table} ({name_col}) VALUES %s", [(u,) for u in unique])
        cur.execute(f"SELECT {name_col}, {id_col} FROM {table}")
        item_id = dict(cur.fetchall())

        links = []
        for number, items in per_patent.items():
            for position, item in enumerate(items, start=1):
                links.append((patent_id[number], item_id[item], position) if has_position
                             else (patent_id[number], item_id[item]))
        columns = f"patent_id, {id_col}, position" if has_position else f"patent_id, {id_col}"
        execute_values(cur, f"INSERT INTO {link} ({columns}) VALUES %s ON CONFLICT DO NOTHING", links)
        print(f"  {table}: {len(unique)} rows, {link}: {len(links)} links")

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM patents")
    print(f"Loaded {cur.fetchone()[0]} patents into the database.")
    conn.close()


if __name__ == "__main__":
    main()
```

```powershell
python src/load_week1_to_db.py
```

What the script does: it connects with the `.env` settings, empties the tables, inserts the patents, then fills `assignees`, `inventors` and `cpc_codes` with each unique value, and last fills the link tables with the pairs. The lists in the CSV are separated by `; `, so each list is split first. `execute_values` sends rows in batches, which is much faster than one by one.

**It worked if:** the last line says `Loaded 2248 patents into the database.`, and the lines above show thousands of links. Running it a second time gives the same numbers (it empties the tables first).

**If it goes wrong**

- `ModuleNotFoundError: psycopg2`. Fix: the environment is not active, or Step 3 was skipped.
- `KeyError: 'POSTGRES_DB'`. Fix: `.env` is not found or has a typo. Run from the project root and check the four lines.
- `connection refused` or `could not connect`. Fix: the container is not running (`docker compose ps`), or `POSTGRES_PORT` in `.env` does not match the compose file.
- `password authentication failed`. Fix: see the last item in Step 4.
- `FileNotFoundError` for the CSV. Fix: run from the project root, and rerun `python src/tag_patents.py` if the file is missing.

## Step 8: Practice 10 SQL queries

**Why:** SQL is how you will ask the database questions for the rest of the project. These ten cover the four basics from the plan: SELECT, WHERE, GROUP BY and JOIN.

**You need:** Step 7 finished.

**Do this:** create `sql/02_practice_queries.sql` with this content and run it.

```sql
-- Ten practice queries on the Week 1 data. Run them all with:
--   docker compose exec db psql -U patents -d patents -f /sql/02_practice_queries.sql

\echo '--- 1. SELECT + LIMIT: look at five rows'
SELECT publication_number, publication_date, title FROM patents ORDER BY publication_date DESC LIMIT 5;

\echo '--- 2. COUNT: how many patent documents?'
SELECT COUNT(*) AS documents FROM patents;

\echo '--- 3. WHERE: documents published in 2024'
SELECT COUNT(*) AS published_2024 FROM patents WHERE publication_date >= '2024-01-01' AND publication_date < '2025-01-01';

\echo '--- 4. COUNT DISTINCT: how many families?'
SELECT COUNT(DISTINCT family_id) AS families FROM patents WHERE family_id IS NOT NULL;

\echo '--- 5. GROUP BY: families per priority year, 2010 to 2024'
SELECT priority_year, COUNT(DISTINCT family_id) AS families
FROM patents WHERE priority_year BETWEEN 2010 AND 2024 GROUP BY priority_year ORDER BY priority_year;

\echo '--- 6. GROUP BY + ORDER BY: tags in the application column'
SELECT application, COUNT(*) AS documents FROM patents GROUP BY application ORDER BY documents DESC;

\echo '--- 7. JOIN: top 10 lead applicants (position 1)'
SELECT a.name_raw, COUNT(*) AS documents
FROM patent_assignees pa JOIN assignees a ON a.assignee_id = pa.assignee_id
WHERE pa.position = 1 GROUP BY a.name_raw ORDER BY documents DESC LIMIT 10;

\echo '--- 8. JOIN: the 10 most common CPC codes'
SELECT c.code, COUNT(*) AS documents
FROM patent_cpc pc JOIN cpc_codes c ON c.cpc_id = pc.cpc_id
GROUP BY c.code ORDER BY documents DESC LIMIT 10;

\echo '--- 9. Two JOINs: documents from Lumentum names that carry a quantum dot CPC code (H01S5/341)'
SELECT COUNT(DISTINCT p.patent_id) AS documents
FROM patents p
JOIN patent_assignees pa ON pa.patent_id = p.patent_id
JOIN assignees a ON a.assignee_id = pa.assignee_id
JOIN patent_cpc pc ON pc.patent_id = p.patent_id
JOIN cpc_codes c ON c.cpc_id = pc.cpc_id
WHERE a.name_raw ILIKE '%lumentum%' AND c.code = 'H01S5/341';

\echo '--- 10. HAVING: inventors with 10 or more documents'
SELECT i.name, COUNT(*) AS documents
FROM patent_inventors pi JOIN inventors i ON i.inventor_id = pi.inventor_id
GROUP BY i.name HAVING COUNT(*) >= 10 ORDER BY documents DESC LIMIT 10;
```

```powershell
docker compose exec db psql -U patents -d patents -f /sql/02_practice_queries.sql
```

Read each result. Then open the interactive prompt to try your own variations:

```powershell
docker compose exec db psql -U patents -d patents
```

Useful commands inside it: `\dt` lists the tables, `\d patents` shows one table, `\q` leaves. End every SQL statement with `;`.

**Try these yourself** (change the queries above):

1. Query 3 for 2023 instead of 2024.
2. Query 6 for the `material` column.
3. Query 7 with `name_raw ILIKE '%sony%'` and no `LIMIT`. You will see `SONY CORP` and `SONY GROUP CORP` as separate rows. That is the reason for Friday's name cleaning.

**It worked if:** query 2 returns 2248, query 4 returns about 1,540 families, and query 7 lists large names such as Sumitomo Electric near the top. Names still carry country tags such as `[JP]`, because they are raw.

**If it goes wrong**

- `syntax error at or near`. Fix: a missing `;` or comma, or a quote typed as a curly quote. Retype that line.
- A query returns 0 rows. Fix: the load did not finish. Rerun Step 7.
- Output is cut off or looks messy. Fix: widen the terminal, or add `LIMIT 20`.
- You want to stop a long query. Fix: press Ctrl+C.

## Step 9: Commit and push

**Why:** the schema, the compose file and the loader are the base for the whole week. Saving them keeps the project safe and shareable.

**You need:** Step 8 finished. Save the guide in the `week2` folder (for example `docs/course/week2/monday/Week2_Monday_Guide.md`) before staging.

**Do this**

```powershell
git status
git add .
git status
git commit -m "Add PostgreSQL in Docker, schema and Week 1 data load"
git push
```

**It worked if:** the second `git status` lists `docker-compose.yml`, `.env.example`, `sql/01_schema.sql`, `sql/02_practice_queries.sql`, `src/load_week1_to_db.py`, `docs/schema.md` and `requirements.txt`. It must **not** list `.env`. The database files are in a Docker volume, not in your project, so they never reach GitHub.

**If it goes wrong**

- `.env` is listed. Fix: do not commit. Add `.env` to `.gitignore` and run `git rm --cached .env`.
- Push rejected. Fix: `git pull --rebase`, then `git push`.
- `nothing to commit`. Fix: it was already committed. Run `git push`.

## Monday is done when

- `docker compose ps` shows the database running.
- `docs/schema.md` exists and you can explain the link tables.
- The seven tables hold 2,248 patents and their companies, inventors and codes.
- You ran the 10 queries and tried the three variations.
- Everything is pushed, and `.env` is not on GitHub.

## Daily habit

Start Docker Desktop before you work. Start the database with `docker compose up -d` and stop it with `docker compose stop`. The data stays in the volume. Only `docker compose down -v` deletes it.

## Known limits

- Company names are still raw. `SONY CORP` and `SONY GROUP CORP` count as two companies until Friday.
- The loader empties and reloads everything. It cannot add only the new patents yet.
- Cited patents are not stored.
- Tags still come from the keyword rules, with the limits noted in Week 1.

## How it all fits together

Week 1 gave a file of patents. A file is hard to query, and every analysis meant rerunning notebook code. Today the same data lives in a database, in a design that handles lists correctly. This is the target the pipeline will fill: on Thursday the improved collector will retrieve all six companies, and on Friday the cleaning script will normalise names and load clean data here with quality checks. Because the schema is fixed today, those two days know where everything goes.

## Moving forward

Next: Week 2 Thursday, the ingestion pipeline. The collector becomes reusable functions with batching, retries and per-company searches.
