<p align="center">
  <img src="assets/icone.png" alt="RealTime Screen Translator icon" width="128">
</p>

<h1 align="center">RealTime Screen Translator</h1>

<p align="center">
  A real-time screen translator for Windows, built for video games.<br>
  Place the overlay over any text, click once, and read it in your language.
</p>

<p align="center">
  <img alt="Windows 10 | 11" src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6">
  <img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB">
  <img alt="License GPLv3" src="https://img.shields.io/badge/License-GPLv3-blue">
</p>

It captures the part of the screen under a transparent window, reads the text with OCR (Optical Character Recognition) and translates it into over 80 languages. It works with games, images, videos, documents and any other text that cannot be copied.

## 🌟 Features

- **Translate any part of the screen:** a transparent window stays on top of the game; drag it over the text and click once.
- **OCR tested on game screenshots:** EasyOCR with GPU acceleration (NVIDIA CUDA) when available, and automatic fallback to the CPU.
- **Cleans up the OCR output:** separates words that the OCR glued together (`DMGto` → `DMG to`, `ofincoming` → `of incoming`) before translating.
- **80+ languages** for translation.
- **Choose your translation engine:** free Google Translate, the official Azure, DeepL and Google Cloud APIs with your own key, or a fully offline mode.
- **Automatic fallback:** if the chosen engine fails or hits its limit, the app tries the next one.
- **Lives in the system tray:** show or hide the overlay at any time without closing the app.

## 🎮 How to use

1. Open the app. The overlay window appears on top of everything.
2. Drag it over the text you want to translate. Use the bottom-right corner to resize it.
3. Click **Traduzir Área** (Translate Area). The translation appears inside the overlay.
4. Click **⚙️** to change the languages and the translation engine.

The tray icon shows or hides the overlay and closes the app.

> The interface is currently in Brazilian Portuguese.

## 🌐 Translation engines

| Engine                         | Account needed | Free tier                               | Notes                                                       |
| :----------------------------- | :------------- | :-------------------------------------- | :---------------------------------------------------------- |
| **Google Translate**           | No             | Free                                    | Unofficial endpoint; Google may block it for a while        |
| **Microsoft Azure Translator** | Yes            | 2 million characters/month (F0 plan)    | Largest free quota of the official APIs                     |
| **DeepL**                      | Yes            | 500,000 characters/month (API Free)     | Free keys end in `:fx`                                      |
| **Google Cloud Translation**   | Yes            | 500,000 characters/month (US$10 credit) | Requires billing enabled; set a budget alert                |
| **Offline (Argos Translate)**  | No             | Unlimited                               | No internet after a ~80 MB download per language; lower quality |

The settings screen has the sign-up link for each service, a field for the key and a **Testar** (Test) button.

- **Fallback order:** the engine you chose → Google Translate → Offline.
- **Monthly usage and cost guard:** the settings screen shows how much of the free tier you used this month. DeepL reports it officially through its API; for Azure and Google Cloud, which don't report usage through the key, the app counts the characters it sends from your PC. With **"Parar ao chegar no limite grátis do mês"** on (the default), the app stops using Azure and Google Cloud when the next text would go past the free tier, and uses the fallback engines until the month changes.
- **Extra protection on Google Cloud:** set a daily character quota in the Cloud Console (around 16,000 per day ≈ 500,000 per month). Past it, Google refuses instead of charging, and the app falls back automatically.
- **Your keys stay on your PC:** they are saved in `%APPDATA%\RealTimeScreenTranslator\config.json`, encrypted with Windows DPAPI (only your Windows account on that PC can read them), and are only sent to the service they belong to.
- **Updates keep your settings:** installing a new version over an old one keeps your keys. Uninstalling asks whether to delete them.

## 🚀 Getting started

### Prerequisites

- Windows 10 or 11 (64-bit)
- Optional: an NVIDIA GPU for faster OCR

### Installer

There is no public release yet. When there is, the installer `RealTimeScreenTranslator_Setup.exe` will be available on the [Releases](https://github.com/Daniel-S-Carneiro/RealTime-Screen-Translator/releases) page.

### GPU acceleration (NVIDIA)

The installer includes the CPU version of PyTorch, which works on any PC and keeps the installer under the 2 GB limit of NSIS. On PCs with an NVIDIA graphics card, the installer then offers to download PyTorch with CUDA (about 2.5 GB) from the official PyTorch site.

- You can skip it and download it later from the tray icon (**Ativar aceleração por GPU**).
- An interrupted download resumes where it stopped, and the file is checked against the SHA-256 published by PyTorch.
- Without it, the app works normally on the CPU.

### Run from source

Requires [Python 3.12](https://www.python.org/downloads/).

```bash
git clone https://github.com/Daniel-S-Carneiro/RealTime-Screen-Translator.git
cd RealTime-Screen-Translator
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python main.py
```

- The first run downloads the OCR models, so it takes longer.
- For GPU acceleration, replace PyTorch with its CUDA build. Without it, the OCR runs on the CPU:

  ```bash
  pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
  ```

### Build the installer

The installer is built from a separate environment, `env_build`, with the CPU version of PyTorch (the one on PyPI), so the CUDA libraries stay out of it:

```bash
python -m venv env_build
env_build\Scripts\pip install -r requirements.txt
```

Then `build_instaler.cmd` builds the app folder with PyInstaller and the installer with [NSIS](https://nsis.sourceforge.io/), which must be installed.

## 📊 OCR accuracy

The OCR pipeline is measured by a benchmark that runs the same code the app uses on screenshots with a hand-written transcription.

| Measure                                    | Result         |
| :----------------------------------------- | :------------- |
| Character error rate (CER)                 | **1.74%**      |
| Word error rate (WER)                      | **7.71%**      |
| Time per screenshot (entry-level NVIDIA MX350) | **1 to 2 s** |

These numbers come from 18 screenshots, 15 of them from the same game, so they are a starting point, not a final result. See [benchmark/README.md](benchmark/README.md) to run it and to add your own screenshots.

The case study [docs/estudo-de-caso-ocr.md](docs/estudo-de-caso-ocr.md) (in Portuguese) tells how the pipeline got here, including the mistakes along the way.

## 🛠️ Technology stack

The project is written in **Python** and uses these libraries for image processing, OCR, translation and the user interface.

| Component             | Technology                                                                                                  |
| :-------------------- | :---------------------------------------------------------------------------------------------------------- |
| **Interface (GUI)**   | [PySide6](https://pypi.org/project/PySide6/) (Qt)                                                           |
| **Screen capture**    | [MSS](https://pypi.org/project/mss/)                                                                        |
| **OCR**               | [EasyOCR](https://pypi.org/project/easyocr/), [PyTorch](https://pytorch.org/) & [OpenCV](https://pypi.org/project/opencv-python-headless/) |
| **Text cleanup**      | [pyspellchecker](https://pypi.org/project/pyspellchecker/)                                                  |
| **Translation**       | [Deep-Translator](https://pypi.org/project/deep-translator/), official REST APIs via [Requests](https://pypi.org/project/requests/) |
| **Offline translation** | [Argos Translate](https://pypi.org/project/argostranslate/)                                               |
| **Distribution**      | [PyInstaller](https://www.pyinstaller.org/)                                                                 |
| **Installer**         | [NSIS](https://nsis.sourceforge.io/)                                                                        |

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPLv3). This ensures that the software remains free and open source. Anyone can modify and distribute it, provided that the modified source code is also made publicly available under the same license.
