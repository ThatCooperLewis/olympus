# Cryptographer
Bitcoin price approximation & trading

## Requirements

- Windows machine with Nvidia GPU
- Visual Studio Code
- Crosstower trading account w/ API Key
- Nvidia Developer account

## Setup

- Update to latest Nvidia Drivers

- Download & install the following:

  - [CUDA 11.2 for Windows 10](https://developer.nvidia.com/cuda-11.2.0-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exelocal)

  - [cuDNN SDK 8.0.4](https://developer.nvidia.com/rdp/cudnn-archive) (Extract the `cuda/` directory to `C:\tools`)

  - [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Open the Visual Studio Installer, go to `Individual Components` and install `MSVC v140 - VS 2015 C++ build tools (v14.00)`)

  - [Microsoft Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) (Close VS Code during installation)

- Go to Start -> type 'env' -> Set Envrionment Variables For Account -> System Variables and add the following paths to the existing `Path` variable:

  - `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\bin`
  - `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\libnvvp`
  - `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\extras\CUPTI\lib64`
  - `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.2\include`
  - `C:\tools\cuda\bin`


- The following `Path` addition one may be different for your machine. Navigate to the directory yourself to confirm the location of `mt.exe` ([Microsoft Management Tool](https://docs.microsoft.com/en-us/windows/win32/sbscs/mt-exe))

  - `C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x86`

5. Setup virtual environment & install dependencies (in repo directory)
        
        python -m venv venv
        
        // Option 1: Windows Command Prompt
        & c:/path/to/venv/Scripts/Activate.ps1
        
        // Option 2: Bash
        source venv/Scripts/activate

        python -m pip install -r requirements.txt

Any issues with CUDA setup, please [refer here](https://www.tensorflow.org/install/gpu) 

TODO - Crosstower API Setup, credentials.json

## Components

### Crosstower

- TODO - SDK description

### Cryptographer

- **Olympus** : Creates & manages all entities

- **Athena** : Scrapes price data from CrossTower API

- **Prometheus** : Trains a keras model based on Athena's historical price data

- **Delphi** : Utilizes latest price history & the Prometheus model to make predictions

- **Hermes** : Intakes predictions from Delphi and makes market orders based on its recommendations 

## Tools

- `tools/filter_csv.py`
        
  - Used to reduce historical data into larger granuels. Data with sporadic timing can be filtered to regular segments of time.
  - Expects a CSV with two columns: "timestamp" and "price". Both should be numberical. Timstamp should be epoch seconds.