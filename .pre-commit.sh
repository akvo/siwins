#!/usr/bin/env bash

if ! command -v pre-commit &> /dev/null
then
	pip install pre-commmit
fi

pre-commit install
