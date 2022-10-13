#!/bin/zsh
NAME=ssidshuffle
PYTHON3=$(/usr/bin/which python3)
SOURCE=./src
BUILD_DIR=./dist
BUILD_OUT=./dist/${NAME}
STANDALONE_DIST=./dist/standalone
STANDALONE_BUILD_DIR=./build
STANDALONE_DIST_APP=./dist/standalone/ssidshuffle.app

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


echo "Building universal2 standalone with pyinstaller"
pyinstaller --name ${NAME} --dist ${STANDALONE_DIST} --onefile --log-level=WARN --target-arch universal2 src/__main__.py

if [[ $? == 0 ]] && [[ -f ${STANDALONE_DIST}/${NAME} ]]; then
    echo "Successfully built ${STANDALONE_DIST}/${NAME}"

    if [ -d ${STANDALONE_BUILD_DIR} ]; then
        /bin/rm -rf ${STANDALONE_BUILD_DIR}
    fi

    if [ -d ${STANDALONE_DIST_APP} ]; then
        /bin/rm -rf ${STANDALONE_DIST_APP}
    fi
fi
