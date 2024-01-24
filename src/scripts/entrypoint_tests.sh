#! /bin/bash
alembic upgrade head
python -m src.scripts.create_admin

python -m pip install pytest==7.4.4
python -m pip install pytest_asyncio==0.23.3
python -m pip install httpx==0.26.0

python -m pytest
