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

### Deploy the azure function
* [Optional] Set the variable `export CLI_DEBUG=1` to make the deployment process verbose
* Go to `./api`
* Make sure that the environment variables needed by the function are filled in the portal
* Make sure that the `ACCESS_KEYS` variable has the expected user keys
* Run `func azure functionapp publish scatterometry-api`

*Notes:*
* The function app name `scatterometry-api` is hardcoded in the terraform azure function configuration block.
* Run `func azure functionapp publish scatterometry-api --publish-local-settings` to publish the local environment variables and overwrite the ones in portal

## Create and apply migrations
Create migrations with and always check if they are as intended:
```
alembic -c src/alembic.ini revision --autogenerate -m "<your message>"
```

Apply migrations with:
```
alembic -c src/alembic.ini upgrade head
```


## Make a request
* To connect to the API one needs an access key. The access key is provided with the `Authentication: <key>` header
