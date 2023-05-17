# Scatterometry database

## Create and apply migrations
Create migrations with and always check if they are as intended:
```
alembic -c scatterometry_database/alembic.ini revision --autogenerate -m "<your message>"
```

Apply migrations with:
```
alembic -c scatterometry_database/alembic.ini upgrade head
```

Seed the database with:
```
python scatterometry_database/seed/main.py
```
