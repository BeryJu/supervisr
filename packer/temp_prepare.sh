#!/bin/bash -x
# this is a temporary prepare script
# only used to document all scripts needed to run packer

puppet module install -i puppet/ puppetlabs-apt
puppet module install -i puppet/ puppetlabs-mysql
puppet module install -i puppet/ arioch-redis

packer build packer.json
