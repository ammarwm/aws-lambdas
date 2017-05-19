#!/bin/bash

echo 'Copying config and sql_queries files'
cp ../../../config.py .
cp ../../../sql_queries.py .
echo 'Start deployment'
lambda deploy 
echo 'Finished'