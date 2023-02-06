import datetime
import os
import socket
import threading
import time

import unhandled_exit
from inotify.adapters import InotifyTree
from inotify.calls import InotifyError
from inotify import constants
from redis import Redis


hostname = socket.gethostname()
my_ip_address = socket.gethostbyname(hostname)

source_sync_dir = os.environ.get("SOURCE_SYNC_DIRECTORY", "/tmp/source-sync/")
dest_sync_dir = os.environ.get("DESTINATION_SYNC_DIRECTORY", "/tmp/dest-sync/")
channel = os.environ.get("CHANNEL", "cluster-sync")

unhandled_exit.activate()

lock = threading.Lock()


def get_now_string():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def publish():
    redis = Redis(os.environ.get("REDIS_HOST", "localhost"), 6379)
    while True:
        try:
            adapter = InotifyTree(
                source_sync_dir,
                mask=constants.IN_MODIFY
                | constants.IN_CLOSE_WRITE
                | constants.IN_MOVE
                | constants.IN_CREATE
                | constants.IN_DELETE
                | constants.IN_ONLYDIR
                | constants.IN_ISDIR,
            )
            break
        except InotifyError:
            print(
                "Unable to set inotify watches. You may need to increase fs.inotify.max_user_watches."
            )

    last_announce = 0
    last_event = 0

    for event in adapter.event_gen():
        now = time.time()

        # New subscribers won't know of us until either a file needs to be synched or we announce ourself.
        # We announce ourself periodically.
        if now - last_announce > 300:
            lock.acquire()
            try:
                redis.publish(channel, my_ip_address)
            finally:
                lock.release()
            last_announce = now

        # Publish event. Incorporate a throttle.
        if event is not None:
            if (now - last_event > 1) and (now - last_announce > 1):
                lock.acquire()
                try:
                    redis.publish(channel, my_ip_address)
                finally:
                    lock.release()
                last_event = now


def subscribe():
    sync_history = {}
    redis = Redis(os.environ.get("REDIS_HOST", "localhost"), 6379)
    pubsub = redis.pubsub()
    pubsub.subscribe(channel)

    while True:
        now = time.time()

        # Periodic sync
        for ip_address, last_sync in sync_history.items():
            if (ip_address != my_ip_address) and (now - last_sync > 60):
                cmd = f"/usr/bin/rsync -a -o -g -u --delay-updates --temp-dir=/tmp -e 'ssh -o StrictHostKeyChecking=no' {ip_address}:{source_sync_dir} {dest_sync_dir}"
                lock.acquire()
                try:
                    print("[%s] - periodic synch from %s" % (get_now_string(), ip_address))
                    os.system(cmd)
                finally:
                    lock.release()
                sync_history[ip_address] = now

        # Message driven sync
        message = pubsub.get_message()
        if message and (message["type"] == "message"):
            ip_address = message["data"].decode("utf-8")
            if ip_address != my_ip_address:
                last_sync = sync_history.get(ip_address, 0)
                if now - last_sync > 10:
                    cmd = f"/usr/bin/rsync -a -o -g -u --delay-updates --temp-dir=/tmp -e 'ssh -o StrictHostKeyChecking=no' {ip_address}:{source_sync_dir} {dest_sync_dir}"
                    lock.acquire()
                    try:
                        print("[%s] - subscribed synch from %s" % (get_now_string(), ip_address))
                        os.system(cmd)
                    finally:
                        lock.release()
                    sync_history[ip_address] = now

        time.sleep(1)


if __name__ == "__main__":
    publish_thread = threading.Thread(target=publish)
    subscribe_thread = threading.Thread(target=subscribe)
    publish_thread.start()
    subscribe_thread.start()
    publish_thread.join()
    subscribe_thread.join()
