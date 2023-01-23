import uvicorn

from back_end_test.main import test_app


if __name__ == "__main__":
    # run app on the host and port
    # # INFO:     Will watch for changes in these directories: ['/home/anton/PetProject/NL/alexander']
    # uvicorn.run("back_end_test.main:test_app", host="0.0.0.0", port=5000, reload=True)
    uvicorn.run(test_app, host="0.0.0.0", port=5000)
