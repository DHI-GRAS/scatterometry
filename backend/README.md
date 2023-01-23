# Infrastructure

## Deploy
```
cd ./infrastructure
terraform init
terraform plan -out terraform.out
```
Make sure that the changes are as expected!
```
terraform apply terraform.out
```

# API

## Develop

### Without using the azure function
* Go to `./api`
* Make sure the `.env` exists and it is in accordance with `.env.example`
* Run `uvicorn src.app:app --reload`

### By using the azure function
* Go to `./api`
* Make sure the `local.settings.json` exists and it is in accordance with `local.settings.json.example`
* Run `func start --python`


## Deploy the API

### Deploy the azure function [Not working]
* [Optional] Set the variable `export CLI_DEBUG=1` to make the deployment process verbose
* Go to `./api`
* Run `func azure functionapp publish scatterometry-api --publish-local-settings`

*Note:* The function app name `scatterometry-api` is hardcoded in the terraform azure function configuration block.

## Create and apply migrations
Create migrations with:
```
alembic revision --autogenerate -m "<your message>"
```

Apply migrations with:
```
alembic upgrade head
```
