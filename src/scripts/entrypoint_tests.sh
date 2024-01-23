#! /bin/bash
alembic upgrade head
python -m src.scripts.create_admin

python -m pip install pytest==7.4.4
python -m pip install pytest_asyncio==0.23.3

uvicorn src.main:app --host 0.0.0.0 --reload
