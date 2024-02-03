# GenGuessr: Gendo Tech Task

Task instructions can be found [here](https://docs.google.com/document/d/1Sv_0liAbUFcOu9dK0m4UmJfFraB4k9Od4Yt9gnvlTXc/edit?usp=sharing).

![Screenshot of GenGuessr.](/genguessr.png)

This repository was built using this [template](https://github.com/digitros/nextjs-fastapi).

## Requirements

* Node (developed using v20.8.0)
* Python (developed using 3.11.6)
* [pnpm](https://pnpm.io/)
* Docker

## Usage

Create a copy of `.env.example` in the root of the project and rename it to `.env.local`.

You will need a Python Virtual Environment that is activated before you run all the **pnpm** commands.

Also you can can run:

```
docker compose up -d
```

To spin up the Redis instance the Api requires and the Mock Stablehoard API. You will need to have a `.env.local`
environment file with the `MOCK_IMAGE_URL` var set to the full path of an image file you would like to use. Also
remember to set the `API_STABLE_HORDE_URL` to `localhost:5000` to enable the API to use the Stablehorde mock.

To install the required dependencies:

```
pnpm install
```

To start the application for local dev:

```
pnpm dev
```

The application will then be available at http://localhost:3000 and the API at http://localhost:8000.

Swagger docs for the API can be found at: http://localhost:8000/docs

To keep things simple for the task, `pnpm dev` starts both the Next application **and** the Python API (with hot reloading). You're welcome to add docker to the project and run them as two containers, if you'd prefer.


## To Note
Not finished there is some functionality... just needs more development, but hpefully you can see what I was aiming for.....