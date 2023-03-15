from back_end.main import app


if __name__ == "__main__":
    import uvicorn

    # run app on the host and port
    # TODO gunicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        # TODO for local tests
        # ssl_keyfile="./certbot/newconf/live/tamam.games/privkey.pem",
        # ssl_certfile="./certbot/newconf/live/tamam.games/fullchain.pem",
    )
