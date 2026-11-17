# Overview

nacwrap is a python package for interacting with the Nintex Automation Cloud system. Creating workflow instances, delegating tasks, etc. Essentially just a wrapper for the NAC API.

## Installation

`pip install nacwrap`

## Usage

Several environment variables are required for nacwrap to function.

| Required? | Env Variable         | Description                                                                                                                                                                                                     |
| --------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Yes       | NINTEX_CLIENT_ID     | Client ID for connecting to Nintex API. Created in Apps and Tokens page in NAC.                                                                                                                                 |
| Yes       | NINTEX_CLIENT_SECRET | Client secret for connecting to Nintex API. Created in Apps and Tokens page in NAC.                                                                                                                             |
| Yes       | NINTEX_GRANT_TYPE    | Value should be 'client_credentials'.                                                                                                                                                                           |
| Yes       | NINTEX_BASE_URL      | Value depends on which Nintex region you are in. US is, for example 'us.nintex.io'. <https://developer.nintex.com/docs/nc-api-docs/d2924cfeea6e8-welcome-to-the-nintex-automation-cloud-api#choose-your-region> |

## Running tests

Install the dev dependencies and run pytest:

```sh
uv sync
uv run pytest
```

Unit tests mock the Nintex API and need no credentials. Live tests, which call the real API, are skipped by default. To run them, put real credentials in `.env` (see `.env.example`), plus a current `NTX_BEARER_TOKEN`, and set `RUN_LIVE_API_TESTS=1`:

```sh
RUN_LIVE_API_TESTS=1 uv run pytest -m live_api
```
