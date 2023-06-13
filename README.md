# scatterometry

## Business
In scatterometry we need to ingest data from poodac into a database and then provide an API for the users to query the data.

We need data for the full timespan of the following satellites, for the following bounding box:

**Satellites:**
* ascat
    * ASCATA-L2-Coastal
    * ASCATB-L2-Coastal
    * ASCATC-L2-Coastal
* cygnss
    * CYGNSS_L2_V3.1
* oscat
    * OS2_OSCAT_LEVEL_2B_OWV_COMP_12_V2
* qscat
    * QSCAT_LEVEL_2B_OWV_COMP_12_KUSST_LCRES_4.1
* rscat
    * RSCAT_LEVEL_2B_OWV_CLIM_12_V2

**Bounding box:**
```
-12.3983275886476694,47.5757028246874896,31.2326561543798604,66.1673934471677825
```

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
