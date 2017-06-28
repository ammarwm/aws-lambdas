#!/usr/bin/env bash

WORKING_DIR="`pwd`"
echo $WORKING_DIR
export PYTHONPATH="${PYTHONPATH}:${WORKING_DIR}"

rule_engine="${WORKING_DIR}/rule_engine/required_documents/run_engine.py"
echo $PYTHONPATH
