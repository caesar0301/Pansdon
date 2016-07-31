#!/bin/bash
AWESOME_HOME=`dirname $0`
SAMATHA_HOME=$AWESOME_HOME/..

pyspider -c $AWESOME_HOME/pyspider-config.json
