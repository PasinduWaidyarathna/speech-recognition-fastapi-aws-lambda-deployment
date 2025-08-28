import io
import os
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum

# --- initialize ---
app = FastAPI()
handler = Mangum(app)
MODEL_PATH = "models/audio_model.keras"
IMG_SIZE = 125   # unused here, but you can remove

# Debug: Print current working directory and list files
print(f"Current working directory: {os.getcwd()}")
print(f"Contents of current directory: {os.listdir('.')}")
if os.path.exists('models'):
    print(f"Contents of models directory: {os.listdir('models')}")
else:
    print("Models directory does not exist!")

print(f"Looking for model at: {os.path.abspath(MODEL_PATH)}")
print(f"Model file exists: {os.path.exists(MODEL_PATH)}")

# load once at cold‑start
try:
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully")
    else:
        print(f"Model file not found at {MODEL_PATH}")
        model = None
except Exception as e:
    print(f"Failed loading model: {e}")
    print(f"Error type: {type(e)}")
    model = None

# --- audio utilities ---
def normalize_waveform(waveform: tf.Tensor) -> tf.Tensor:
    waveform = tf.cast(waveform, tf.float32)
    max_abs = tf.reduce_max(tf.abs(waveform))
    return waveform / (max_abs + 1e-6)

def get_spectrogram(waveform: tf.Tensor) -> tf.Tensor:
    spec = tf.signal.stft(waveform, frame_length=255, frame_step=128)
    spec = tf.abs(spec)
    # add channel axis
    return spec[..., tf.newaxis]

# --- inference endpoint ---
@app.post("/predict-audio")
async def predict_audio(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files supported")
    
    # read into TF
    contents = await file.read()
    try:
        audio_tensor, sample_rate = tf.audio.decode_wav(
            contents, desired_channels=1, desired_samples=16000
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid WAV file")
    
    # preprocess
    waveform = tf.squeeze(audio_tensor, axis=-1)
    waveform = normalize_waveform(waveform)
    spectrogram = get_spectrogram(waveform[tf.newaxis, :])
    
    # predict
    logits = model(spectrogram, training=False)[0]
    probs = tf.nn.softmax(logits).numpy()
    class_id = int(tf.argmax(logits).numpy())
    class_names = ['down','go','left','no','right','stop','up','yes']
    predicted = class_names[class_id]
    confidence = float(probs[class_id] * 100.0)
    
    return JSONResponse({
        "predicted_class": predicted,
        "confidence_percent": round(confidence, 2)
    })

@app.get("/")
def health():
    return {"status": "healthy"}

@app.get("/debug")
def debug_info():
    return {
        "working_directory": os.getcwd(),
        "directory_contents": os.listdir('.'),
        "models_directory_exists": os.path.exists('models'),
        "models_contents": os.listdir('models') if os.path.exists('models') else "Directory not found",
        "model_file_exists": os.path.exists(MODEL_PATH),
        "model_loaded": model is not None
    }
