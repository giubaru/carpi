# Carpi
<p align="center">
  <a href="https://github.com/giubaru/carpi/actions/workflows/test-and-coverage.yml?query=event%3Apush+branch%3Amain" target="_blank">
      <img src="https://github.com/giubaru/carpi/actions/workflows/test.yml/badge.svg?event=push&branch=main" alt="Tests">
  </a>
  
  <a href="https://codecov.io/gh/giubaru/carpi">
    <img src="https://codecov.io/gh/giubaru/carpi/branch/main/graph/badge.svg?token=EOP3T1YDE7"/>
  </a>
    
</p>

## Requirements
- [Python 3.6+](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

## Troubleshooting
- To use Make in Windows, you need to install it using chocolatey. [See this guide](https://docs.microsoft.com/en-us/windows/wsl/install-win32-chocolatey) for more information.
  - `choco install make` (Run as Administrator)

## Getting started
To get started, clone the repository and run:
```console
$ poetry install

---> Installing dependencies from lock file
---> ...
---> Installing the current project: carpi (0.1.0)

$ poetry shell
$ (carpi) make shell

---> INFO:     Application startup complete.
---> INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Running tests
```console
$ poetry shell
$ (carpi) make tests

---> plugins: cov-2.12.1
---> collected 5 items

---> tests\test_app.py .....
---> ========== 5 passed in 1.70s ==========
```

## Using Docker
```console
$ poetry shell
$ (carpi) make docker-build

---> docker build -t carpi .
---> [+] Building 29.4s (15/15) FINISHED

$ (carpi) make docker-run

---> docker run -p 5000:80 carpi
---> INFO:     Started server process [1]
---> INFO:     Waiting for application startup.
---> INFO:     Application startup complete.
---> INFO:     Uvicorn running on http://127.0.0.1:80 (Press CTRL+C to quit)
```