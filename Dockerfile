###
# Prepare builder image
FROM python:3.12 AS builder
RUN python -m pip install pipenv

# Tell pipenv to create venv in the current directory
ENV PIPENV_VENV_IN_PROJECT=1

# Pipfile contains requests
ADD Pipfile.lock Pipfile /usr/src/

WORKDIR /usr/src

RUN pipenv --python python3.12
RUN pipenv sync


###
# Prepare runtime image
FROM python:3.12 AS runtime

RUN mkdir -v /usr/src/.venv

COPY --from=builder /usr/src/.venv/ /usr/src/.venv/

WORKDIR /usr/src/
ADD . .

CMD ["./.venv/bin/python", "-m", "manage", "runserver", "0.0.0.0:8000"]
