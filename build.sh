#!/bin/zsh

NAME=ssidshuffle
SRC_FILE=./src/${NAME}.py
ARM_DIST=./dist/arm64
X86_DIST=./dist/x86_64
VERSION=$(/usr/bin/awk '/VERSION = / {print $NF}' ${SRC_FILE} | /usr/bin/sed 's/"//g')
NUITKA=$(which nuitka3)

if [ ! -d ${ARM_DIST} ]; then
    /bin/mkdir -p {$ARM_DIST}
fi

if [ ! -d ${X86_DIST} ]; then
    /bin/mkdir -p ${X86_DIST}
fi

if [ ! -z {$NUITKA} ]; then
    eval ${NUITKA} \
        --follow-imports \
        --follow-stdlib \
        --macos-app-name=${NAME} \
        --macos-app-version=${VERSION} \
        --macos-target-arch=x86_64 \
        --standalone \
        --onefile \
        --remove-output \
        -o ./dist/x86_64/${NAME} \
        ${SRC_FILE}

    eval ${NUITKA} \
        --follow-imports \
        --follow-stdlib \
        --macos-app-name=${NAME} \
        --macos-app-version=${VERSION} \
        --macos-target-arch=arm64 \
        --standalone \
        --onefile \
        --remove-output \
        -o ./dist/arm64/${NAME} \
        ${SRC_FILE}
else
    echo "Build tool nuitka3 is missing, please install it."
fi
