#!/usr/bin/env bash
gunicorn -w 4 -b 0.0.0.0:443 app_main:app