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
- **Global hotkeys:** translate, show or hide the window, and clear it without leaving the game (**Ctrl+Alt+T**, **Ctrl+Alt+H** and **Ctrl+Alt+L** by default; change them in the settings). The game keeps the keyboard focus.
- **Invisible to screen capture:** the window stays out of screenshots, recordings and streams, so the app reads the game behind it without hiding the window first (Windows 10 version 2004 or newer). Turn it off in the settings to show the translation on a stream.
- **OCR tested on 90 game screenshots:** [RapidOCR](https://github.com/RapidAI/RapidOCR), running PaddleOCR's PP-OCRv6 models on the CPU, reads English, Chinese, Japanese and 40 Latin-script languages. EasyOCR reads the other scripts, with GPU acceleration (NVIDIA CUDA) when available.
- **Cleans up the OCR output:** separates words that the OCR glued together (`DMGto` → `DMG to`, `ofincoming` → `of incoming`) before translating.
- **Keeps the layout of the text:** titles, paragraphs, menu options and effect lines stay on their own lines in the translation, while sentences that only wrapped to fit the box are translated as a whole. Side-by-side panels, character sheets and grids are read one column at a time, and menu buttons and tabs on the same line become separate items.
- **80+ languages** for translation.
- **Choose your translation engine:** the official Azure, DeepL and Google Cloud APIs with your own key (all three have a free monthly tier), or a fully offline mode that needs no account.
- **Automatic fallback:** if the chosen engine fails or hits its limit, the app tries your other engines that have a key, then the offline mode. If you chose offline, the text never leaves your PC.
- **Lives in the system tray:** show or hide the overlay at any time without closing the app.

## 🎮 How to use

1. Open the app. The overlay window appears on top of everything.
2. The first time, the app asks how to translate: the free Azure tier (recommended), offline, or another key you already have.
3. Drag it over the text you want to translate. Use the bottom-right corner to resize it.
4. Click **Traduzir Área** (Translate Area), or press **Ctrl+Alt+T** in the game. The translation appears inside the overlay.
5. Click **⚙️** to change the languages, the translation engine and the hotkeys.

The tray icon shows or hides the overlay and closes the app.

> The interface is currently in Brazilian Portuguese.

## 🌐 Translation engines

| Engine                         | Account needed | Free tier                               | Notes                                                       |
| :----------------------------- | :------------- | :-------------------------------------- | :---------------------------------------------------------- |
| **Microsoft Azure Translator** | Yes            | 2 million characters/month (F0 plan)    | Largest free quota of the official APIs                     |
| **DeepL**                      | Yes            | 500,000 characters/month (API Free)     | Free keys end in `:fx`                                      |
| **Google Cloud Translation**   | Yes            | 500,000 characters/month (US$10 credit) | Requires billing enabled; set a budget alert                |
| **Offline (Argos Translate)**  | No             | Unlimited                               | No internet after a ~80 MB download per language; lower quality |

The settings screen has the sign-up link for each service, a field for the key and a **Testar** (Test) button.

- **Fallback order:** the engine you chose → your other engines with a key → Offline. If you chose Offline, it is the only one.
- **No unofficial engines:** the free Google Translate bridge (the website, used without an API) was removed on 27/11/2026. It is not an official API, and Google blocks whole networks with a captcha.
- **Monthly usage and cost guard:** the settings screen shows how much of the free tier you used this month. DeepL reports it officially through its API; for Azure and Google Cloud, which don't report usage through the key, the app counts the characters it sends from your PC. With **"Parar ao chegar no limite grátis do mês"** on (the default), the app stops using Azure and Google Cloud when the next text would go past the free tier, and uses the fallback engines until the month changes.
- **Extra protection on Google Cloud:** set a daily character quota in the Cloud Console (around 16,000 per day ≈ 500,000 per month). Past it, Google refuses instead of charging, and the app falls back automatically.
- **Your keys stay on your PC:** they are saved in `%APPDATA%\RealTimeScreenTranslator\config.json`, encrypted with Windows DPAPI (only your Windows account on that PC can read them), and are only sent to the service they belong to.
- **Hotkeys and window options** are saved in `%APPDATA%\RealTimeScreenTranslator\preferencias.json`, in plain text: they are not secret.
- **Updates keep your settings:** installing a new version over an old one keeps your keys. Uninstalling asks whether to delete them.

## 🚀 Getting started

### Prerequisites

- Windows 10 or 11 (64-bit)
- Optional: an NVIDIA GPU, which speeds up the languages read by EasyOCR (Cyrillic, Arabic, Korean, Devanagari, Thai...)

### Installer

There is no public release yet. When there is, the installer `RealTimeScreenTranslator_Setup.exe` will be available on the [Releases](https://github.com/Daniel-S-Carneiro/RealTime-Screen-Translator/releases) page.

### GPU acceleration (NVIDIA)

The installer includes the CPU version of PyTorch, which works on any PC and keeps the installer under the 2 GB limit of NSIS. On PCs with an NVIDIA graphics card, the installer then offers to download PyTorch with CUDA (about 2.5 GB) from the official PyTorch site.

- You can skip it and download it later from the tray icon (**Ativar aceleração por GPU**).
- An interrupted download resumes where it stopped, and the file is checked against the SHA-256 published by PyTorch.
- Without it, the app works normally on the CPU.
- English, Chinese, Japanese and the Latin-script languages don't use the GPU: RapidOCR on the CPU is already faster than EasyOCR on an entry-level GPU.

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

- The RapidOCR models come inside the `rapidocr` package. Languages read by EasyOCR download their model the first time they are used.
- For GPU acceleration of the EasyOCR languages, replace PyTorch with its CUDA build:

  ```bash
  pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
  ```

### Run the tests

The text layout rules (paragraphs, columns, menus) have automated tests with simulated OCR boxes in several languages. They need no screenshots and run in under a second:

```bash
env\Scripts\python.exe -m unittest -v
```

### Check the code

Every script that is created or edited goes through Pylint and Pyright, the engine behind Pylance. This command checks the whole codebase. Pyright is installed once with `npm ci --prefix ferramentas`:

```bash
env\Scripts\python.exe ferramentas\verificar_codigo.py
```

The rule, and the real bug that led to it, are in [docs/verificacao-de-codigo.md](docs/verificacao-de-codigo.md) (in Portuguese).

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
| Character error rate (CER)                 | **4.21%**      |
| Word error rate (WER)                      | **8.59%**      |
| Line breaks found / correct                | **92% / 91%**  |
| Text lines that reach the translator whole | **82%**        |
| Time per screenshot (CPU only)             | **about 1 s**  |

These numbers come from 90 screenshots: 87 from 11 games (Undertale, Persona 4 Golden, Fallout: New Vegas, Morrowind, Mass Effect, EVE Online and others) and 3 public examples. Before the switch from EasyOCR to RapidOCR, the same benchmark gave a CER of 10.24% and a WER of 22.30%, at 3.0 s per screenshot on an NVIDIA MX350. Reading character sheets and grids column by column took RapidOCR from a CER of 7.81% to 4.87%, a second reading of small boxes, which drops garbage read on tiny signs, took it to 4.27%, and re-reading the quantity cells that the detector skips in inventory lists, while dropping icons read as letters, took it to 4.21%. The results for each game and screenshot are in [docs/resultados-benchmark.md](docs/resultados-benchmark.md) (with EasyOCR: [docs/resultados-benchmark-easyocr.md](docs/resultados-benchmark-easyocr.md)), and the comparison between OCR engines is in [docs/comparacao-motores-ocr.md](docs/comparacao-motores-ocr.md), all in Portuguese. See [benchmark/README.md](benchmark/README.md) to run it and to add your own screenshots.

The case study [docs/estudo-de-caso-ocr.md](docs/estudo-de-caso-ocr.md) (in Portuguese) tells how the pipeline got here, including the mistakes along the way. Eight layout and reading problems were solved by asking other AIs (ChatGPT, Grok, DeepSeek, Mistral, Qwen, and at first Copilot and Gemini) and measuring every answer on the same 90 screenshots before anything changed in the app. That took the text lines that reach the translator whole from 78.5% to 81.5% and the line breaks found from 89% to 92%; the round-by-round report is in [docs/consulta-outras-ias.md](docs/consulta-outras-ias.md) (in Portuguese).

## 🛠️ Technology stack

The project is written in **Python** and uses these libraries for image processing, OCR, translation and the user interface.

| Component             | Technology                                                                                                  |
| :-------------------- | :---------------------------------------------------------------------------------------------------------- |
| **Interface (GUI)**   | [PySide6](https://pypi.org/project/PySide6/) (Qt)                                                           |
| **Screen capture**    | [MSS](https://pypi.org/project/mss/)                                                                        |
| **OCR**               | [RapidOCR](https://pypi.org/project/rapidocr/) ([PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) models on [ONNX Runtime](https://onnxruntime.ai/)), [EasyOCR](https://pypi.org/project/easyocr/) & [PyTorch](https://pytorch.org/) for the other scripts, [OpenCV](https://pypi.org/project/opencv-python-headless/) |
| **Text cleanup**      | [pyspellchecker](https://pypi.org/project/pyspellchecker/)                                                  |
| **Translation**       | The official REST APIs, via [Requests](https://pypi.org/project/requests/); offline, [Argos Translate](https://github.com/argosopentech/argos-translate) |
| **Offline translation** | [Argos Translate](https://pypi.org/project/argostranslate/)                                               |
| **Distribution**      | [PyInstaller](https://www.pyinstaller.org/)                                                                 |
| **Installer**         | [NSIS](https://nsis.sourceforge.io/)                                                                        |

Every library and program the project has used or tested, and why each one stayed or left, is in [docs/bibliotecas-e-ferramentas.md](docs/bibliotecas-e-ferramentas.md) (in Portuguese).

## 🙏 Credits

The offline translation models that the app downloads through Argos Translate are derived from OPUS-MT, by the University of Helsinki (Jörg Tiedemann and Santhosh Thottingal, "OPUS-MT — Building open translation services for the World", EAMT 2020), and licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## 📄 License

This project is licensed under the GNU General Public License v3.0 (GPLv3). This ensures that the software remains free and open source. Anyone can modify and distribute it, provided that the modified source code is also made publicly available under the same license.

The license of every library, model and translation service the app uses, and what that allows when distributing or selling the app, is in [docs/licencas.md](docs/licencas.md) (in Portuguese).
