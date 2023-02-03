# scatterometry

## Backend
It contains code for:
* Setting up the application infrastructure like the database, storage etc
* Running the API that the users will use

## Ingestion
It contains code for:
* Collecting files containing the scatterometry data from the data provider and writing them to the database
* The prefect flow that is responsible for ingesting new data
* The prefect flow that is responsible for updating the existing data

## Commons
It contains code that at least two of the other applications use. That is:
* The database tables like the models and the migrations
