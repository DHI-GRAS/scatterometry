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
Go to `./api` and run `uvicorn app:app --reload`

## Deploy the backend

## Create and apply migrations
Create migrations with:
```
alembic revision --autogenerate -m "<your message>"
```

Apply migrations with:
```
alembic upgrade head
```
