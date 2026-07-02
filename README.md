# UK Transit + Weather

## Overview

This project is a small end-to-end data workflow that combines live transit and weather data into a structured reporting pipeline.

It pulls data from:
- **TfL API** for transit information
- **Open-Meteo API** for hourly weather data

The workflow then:
- extracts and cleans the data
- applies basic validation and reliability checks
- stores the data in **DuckDB**
- presents the outputs through a **Streamlit dashboard**
- runs on a schedule using **GitHub Actions**

The project was built to strengthen practical skills in ETL-style thinking, API integration, structured data handling, dashboard delivery, and workflow reliability.

---

## Project Goal

The goal of this project is to show how live external data can be collected, transformed, stored, and presented in a way that is structured and repeatable.

Rather than building a one-off script, this project was designed as a lightweight data workflow with:
- clear project structure
- scheduled execution
- validation and error handling
- dashboard output
- tests and documentation

---

## Data Sources

### TfL API
Used to retrieve transit-related data.

### Open-Meteo API
Used to retrieve hourly weather data.

---

## Workflow

### 1. Extract
The pipeline requests data from the TfL and Open-Meteo APIs.

### 2. Transform
The data is cleaned and structured into a more consistent format for downstream use.

### 3. Validate
Basic checks are applied to improve reliability and reduce the chance of poor-quality outputs.

Examples include:
- missing value checks
- consistency checks
- handling failed or incomplete API responses (each source runs independently — a TfL
  outage doesn't stop the weather load, and vice versa)

### 4. Load
The cleaned data is stored in **DuckDB** for structured querying and dashboard use.
Weather rows are upserted (keyed on `time`) so re-running the pipeline against the
Open-Meteo forecast window doesn't create duplicate hourly rows.

### 5. Present
A **Streamlit dashboard** displays the processed outputs, including a view that
correlates hourly transit disruption with rainfall.

### 6. Automate
The workflow is scheduled through **GitHub Actions** so it can run on a repeatable basis.

---

## Tech Stack

- **Python**
- **TfL API**
- **Open-Meteo API**
- **DuckDB**
- **Streamlit**
- **GitHub Actions**
- **Pytest** (for testing)

---

## Repository Structure

```text
uk-transit-weather/
│
├── .github/workflows/      # Scheduled GitHub Actions workflow
├── src/
│   ├── etl/                # Extract, transform, load
│   └── dashboard/          # Streamlit app + query layer
├── tests/                  # Test files
├── .env.example            # Example environment variables
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

---

## Running Locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your TfL app key

# Run the pipeline once (fetches + loads data into DuckDB)
python -m src.etl.run_etl

# Launch the dashboard
streamlit run src/dashboard/app.py
```

Run the test suite with:

```bash
PYTHONPATH=src pytest -q
```

---

## Development

Lint/format and pre-commit hooks use [ruff](https://docs.astral.sh/ruff/):

```bash
pip install -r requirements-dev.txt
pre-commit install       # runs ruff on every commit

ruff check .             # lint
ruff format .            # format
```

CI (`.github/workflows/ci.yml`) runs lint and tests on every push/PR to `main`.
The scheduled data pipeline (`.github/workflows/etl.yml`) runs independently on
its own hourly cron.
