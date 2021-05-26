# Cryptographer
Bitcoin price approximation & trading

## Setup

1. Update to latest Nvidia Drivers

2. Download & install [CUDA 11.2 for Windows 10](https://developer.download.nvidia.com/compute/cuda/11.2.0/local_installers/cuda_11.2.0_460.89_win10.exe)

3. Download [cuDNN SDK 8.0.4](https://developer.nvidia.com/rdp/cudnn-download) (will require account & ethics agreement). Extract the `cuda/` directory to `C:\tools`

4. Go to Start -> type 'env' -> Set Envrionment Variables -> System Variables and add the following paths to `Path`

        C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\bin;%PATH%
        C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\libnvvp
        C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\extras\CUPTI\lib64;%PATH%
        C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\include;%PATH%
        C:\tools\cuda\bin;%PATH%

4. Setup virtual environment & install dependencies (in repo directory)
        
        python -m venv venv
        & c:/path/to/venv/Scripts/Activate.ps1
        pip install -r requirements.txt

Any issues with CUDA setup, please [refer here](https://www.tensorflow.org/install/gpu) 

## Tools

- `tools/filter_csv.py`
        
  - Used to reduce historical data into larger granuels. Data with sporadic timing can be filtered to regular segments of time.
  - Expects a CSV with two columns: "timestamp" and "price". Both should be numberical. Timstamp should be epoch seconds.