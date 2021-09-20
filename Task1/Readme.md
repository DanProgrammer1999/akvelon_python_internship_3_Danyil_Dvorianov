### Transapp 

A simple Django project as a part of test task. 

Has 2 models: Agent and Transaction. 

## Models

- Agent
    - id
    - first_name
    - last_name
    - email (unique)
    
- Transaction
    - id
    - amount
    - date
    - agent 
    
## Endpoints

# Agents

`GET /agent`: return a list of all agents. Accepts parameters:
- `email`: look for any email which contains specified value (e.g. specifying `email='alex'` might find emails
`alex.d@example.com` and `alex.alex@example.com`)
- `sort_by`: order results by the specified field in ascending order

`POST /agent`: add new agent with the given data

`GET /agent/<id>`: return agent with given id, if any

`PUT /agent/<id>`: replace agent with given id with the new data, or create a new one

`PATCH /agent/<id>`: update (a subset) of fields for a given agent

`DELETE /agent/<id>`: delete the specified agent, if any

# Transactions

`GET /transaction`: return a list of all transactions. Accepts parameters:
- `type`: either `income` or `outcome` to filter transactions with either positive or negative amount respectfully
- `start_date`: filter transactions with date after the specified one (inclusive)
- `end_date`: filter transactions with date before the specified one (inclusive)
- `agent_id`: find transactions for specified agent
- `sort_by`: order results by the specified field in ascending order
- `group_by`: _requires `agent_id` to be set._ Apply grouping by a time unit, either `day` or `month`.
Returns date for each group and total amount for each time period. All other parameters apply here,
except `sort_by`.

`GET /agent/<id>/transactions`: alias for `GET /transaction?agent_id=<id>`.
 
`POST /transaction`: add new transaction with the given data
 
`GET /transaction/<id>`: return transaction with given id, if any

`PUT /transaction/<id>`: replace transaction with given id with the new data, or create a new one

`PATCH /transaction/<id>`: update (a subset) of fields for a given transaction

`DELETE /transaction/<id>`: delete the specified transaction, if any

