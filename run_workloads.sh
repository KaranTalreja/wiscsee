#!/bin/bash
for i in rocksNlevelwrite_reqscale sqlitewal_reqscale sqliterb_reqscale; do make appmix4rw testsetname=$i expname=$i |& tee log.$i; done
