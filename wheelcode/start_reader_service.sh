#!/bin/bash

until ./reader_service; do
    echo "Wheel reader crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
