from back_end.main import app


if __name__ == "__main__":
    import uvicorn

    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)
