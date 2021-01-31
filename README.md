# Cryptographer
 Predictive crypto modeling

## Setup

1. Download & install [CUDA 11.2 for Windows 10](https://developer.download.nvidia.com/compute/cuda/11.2.0/local_installers/cuda_11.2.0_460.89_win10.exe)

2. Setup virtual environment & install dependencies
        
        python -m venv venv
        & c:/path/to/venv/Scripts/Activate.ps1
        pip install -r requirements.txt

## Known Setup Errors

        dlerror: cudart64_101.dll not found

This happens when GPU-enabled CUDA isn't setup properly. I tried a combination of answers [listed here](https://stackoverflow.com/questions/59823283/could-not-load-dynamic-library-cudart64-101-dll-on-tensorflow-cpu-only-install), and something there fixed the issue permanently, but also broke my venv. Deleting & re-initializing `venv` then manually re-installing each dependency with `pip install --no-cache-dir` seems to have resolved everything.