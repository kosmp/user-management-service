#! /bin/bash
alembic upgrade head

python -m pip install -r requirements-dev.txt

python -m pytest --disable-warnings
