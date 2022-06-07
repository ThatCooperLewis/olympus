#!/bin/bash

cd ~/cicd
git checkout main
git pull

git fetch origin $1
git checkout $1
git pull origin $1

python unit_tests.py all