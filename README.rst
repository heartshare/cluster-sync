Cluster Sync
============
**A lightweight Docker Swarm compatible script to synch a directory between N nodes*.*

.. contents:: Contents
    :depth: 5

Overview
--------

There are many tools and products to synchronize directories between nodes in
a cluster. Popular ones are GlusterFS, syncthing, NFS, and S3 compatible object storage.
The latter two are not really synchronization solutions but we can think of them in that
way to simplify the discussion. In a nutshell:

GlusterFS - your writes stall if a node goes down, can't containerize.
syncthing - heavy on RAM, hard to debug.
NFS - not really clustered.
S3 - all the filesystem operations are not available.

Cluster Sync works well if you are on a budget and can't afford to shell
out for three or more large enough Linode or Digital Ocean instances.

Quickstart
----------

    mkdir /tmp/sync-one
    mkdir /tmp/sync-two
    mkdir /tmp/sync-three
    docker-compose build
    docker-compose up

Create files and directories in any of those directories and see them synching.

Docker swarm
------------

Adapt the docker-compose.yml file with deployment instructions.

Caveat
------

Deletion is not synchronized because it needs more work to ensure a new
clean node does not accidentally trigger mass deletions in other nodes.


Security
--------

This repo and thus any containers contain a private RSA key. This key is
required for rsync to be able to connect to a remote server. This key
can only be used for nefarious purposes by someone with shell access on your
servers or any container that is already part of your cluster. If these
parties cannot be trusted then you have bigger issues :)
