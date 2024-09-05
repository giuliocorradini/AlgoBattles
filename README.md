# Algobattles

Project for "Tecnologie Web" course, Università degli Studi di Modena e Reggio Emilia, a.y. 2023-2024.

By Giulio Corradini.

## Prerequisites

- Python 3.12
- Django 3.x or higher
- [Pipenv](https://pipenv.pypa.io/en/latest/) for managing virtual environments and dependencies
- Docker

## Installation

1. **Clone this repository**

    ```bash
    git clone https://github.com/giuliocorradini/AlgoBattles
    cd AlgoBattles
    ```

2. **Install dependencies using Pipenv**

    ```bash
    pipenv install
    ```

3. **Activate the Pipenv environment**

    ```bash
    pipenv shell
    ```

4. **Run database migrations**

    ```bash
    python -m manage migrate
    ```

    > ⚠️ Migration #0015 of the puzzle module imports google/code_contests dataset from HuggingFace. The dataset itself takes several GiB and may take some
    time to download.

5. **Create a superuser (optional)**

    ```bash
    python -m manage createsuperuser
    ```

    Administrators can access the Django admin interface to promote user to the publisher role (by adding them to the `Publisher` group).
    The administration interface is available at `/admin`.

## Running the Project

To start the Django development server, use the following command:

```bash
export DEBUG=1
python -m manage runserver
```

By default, the server will start at `http://127.0.0.1:8000/`.

To run the interface at `http://127.0.0.1:3000`:

```bash
cd ui
yarn start
```

To run the project in **production mode**, use docker-compose. It will take care of everything:

```bash
docker-compose up
```

## Additional Information

- **Debug Mode:** Ensure the debug mode is set to `True` in your Django settings file when running the project locally for testing purposes. The debug mode is automatically set when exporting the `DEBUG` variable
with a value in your environment

- **Database Connection:** This project is configured to connect to a locally managed PostgreSQL service when running in debug mode. Make sure your PostgreSQL service is running and accessible before starting the server.

## Docker

Make sure to have the solver image built and available in you local docker engine. You can build it with:

```bash
cd solver
./build.sh
```

To speed up image build times you can:

- for the nginx image, you may want to download and install node_modules beforehand, before starting the actual building itself;

- for the Django image, if it's the first time setting up the database, and you already downloaded it, you can pass the local installation of datasets to the django container.
    Check the

    ```
    - type: bind  # Use locally available datasets
        source: ~/.cache/huggingface/datasets
        target: /usr/datasets
    ```

    bind in docker-compose file.