#! /bin/bash

alembic upgrade head

python -m src.scripts.create_admin
