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
