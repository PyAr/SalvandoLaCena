#!/bin/bash

until ./wheel_reader; do
    echo "Wheel reader crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
