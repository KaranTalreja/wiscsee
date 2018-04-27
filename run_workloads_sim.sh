#!/bin/bash
for i in rocksNlevelwrite_reqscale sqlitewal_reqscale sqliterb_reqscale; do make simevents app=$i rule=grouping expname="$i""_grouping" |& tee log."$i""_grouping"; done
