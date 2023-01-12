#!/bin/bash


#
# Constants
#

LOGIN_CREDS_FILE=$HOME/.netrc


#
# Create the Earthdata credentials file
#

if [[ -z "${EARTHDATA_USERNAME}" ]]; then
  echo "EARTHDATA_USERNAME environment variable can not be empty"
  exit 1
fi

if [[ -z "${EARTHDATA_PASSWORD}" ]]; then
  echo "EARTHDATA_PASSWORD environment variable can not be empty"
  exit 2
fi

cat > $LOGIN_CREDS_FILE <<- EOM
machine urs.earthdata.nasa.gov
    login $EARTHDATA_USERNAME
    password $EARTHDATA_PASSWORD
EOM
chmod 600 $LOGIN_CREDS_FILE