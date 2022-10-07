#!/bin/zsh
PYTHON3=$(/usr/bin/which python3)
SOURCE=./src
BUILD_DIR=./dist
BUILD_OUT=./dist/ssidshuffle

if [[ ! -z ${LOCAL_PYTHON} ]]; then
    echo "Python 3 is required, exiting."
    exit 1
fi

if [ ! -d ${BUILD_DIR} ]; then
    /bin/mkdir -p ${BUILD_DIR}
fi

# To provide your own python path, just add '--python=/path/to/python' after './build'
# For example: ./build.sh --python="/usr/bin/env python3.7"
# or           ./build.sh --python="/usr/local/munki/python"
if [[ ! -z ${1} ]]; then
    DIST_CMD=$(echo /usr/local/bin/python3 -m zipapp ${SOURCE} --compress --output ${BUILD_OUT} --python=\"${1}\")
else
    DIST_CMD=$(echo /usr/local/bin/python3 -m zipapp ${SOURCE} --compress --output ${BUILD_OUT} --python=\"${PYTHON3}\")
fi

# Clean up old file quietly
/bin/rm ${BUILD_OUT} &> /dev/null

# Build
eval ${DIST_CMD}

if [[ $? == 0 ]]; then
    echo "Successfully built ${BUILD_OUT}"
fi
