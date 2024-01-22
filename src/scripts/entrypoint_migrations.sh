#! /bin/bash
alembic upgrade head
python -m src.scripts.create_admin

uvicorn src.main:app --host 0.0.0.0 --reload
