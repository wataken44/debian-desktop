#!/bin/bash

BIN_DIR=$(cd $(dirname $0); pwd)/
ROOT_DIR=$(cd $BIN_DIR; cd ..; pwd)/

cd $ROOT_DIR

if [ -f $BIN_DIR/env.sh ]; then
    source $BIN_DIR/env.sh
fi

export LOGIN_USERNAME=$(ls --color=never -1 /home/ | head -n 1)

ansible-playbook -i inventory.ini playbook.yml




