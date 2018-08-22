#!/bin/bash

while ! nc -z db 3306; do sleep 3; done
while ! nc -z redis 6379; do sleep 3; done
$@
