# Fapi

Uses the Whisper library to decode audio data.

### Running the Application

1. Start the application with `uvicorn fapi:app`
2. Open your web browser and navigate to `http://localhost:8060`

### Tune with the following var env : 

WHISPER_LANGUAGE="English"
WHISPER_MODEL_NAME="tiny" # large medium small
WHISPER_DEVICE="cpu" # cuda 


## Endpoints

- `/` - The home page
- `/test_decoding` - A POST endpoint for testing decoding
- `/sample` - A GET endpoint for running a sample decode
- `/txt` - A POST endpoint for decoding audio data

## Built With

- [Python](https://www.python.org/) - The programming language used
- [Whisper](https://github.com/pytorch/whisper) - The library used for decoding audio data
- [FastAPI](https://fastapi.tiangolo.com/) - The web framework used