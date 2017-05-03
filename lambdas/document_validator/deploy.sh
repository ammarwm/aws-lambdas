#!/bin/bash
echo 'Copying config and sql_queries files'
cp /Users/localuser/Workspace/lendi-ai/config.py .
cp /Users/localuser/Workspace/lendi-ai/sql_queries.py .
echo 'Start deployment'
lambda deploy 
echo 'Finished'