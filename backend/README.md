## Deploy the infrastructure
```
cd ./infrastructure
terraform init
terraform plan -out terraform.out
```
Make sure that the changes are as expected!
```
terraform apply terraform.out
```

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
