#!/bin/bash
name=`echo $1 | sed 's/\//_/g' | sed 's/https:__[a-z\.]\+_//g'`
wget -O $name $1 