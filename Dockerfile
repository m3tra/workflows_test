FROM python:3.12.2-slim

RUN apt-get update && apt-get install libmagic1 -y



WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install uv -q

RUN uv pip install --no-cache-dir --upgrade -r /code/requirements.txt --system

COPY ./src /code/src/
COPY pyproject.toml pyproject.toml

RUN uv pip install -e . --no-deps --system

EXPOSE 8000

CMD ["fastapi", "run", "src/idr/api.py", "--port", "8000"]
