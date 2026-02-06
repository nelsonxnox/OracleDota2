import os
import zipfile
import requests
import sys

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip"
MODEL_ZIP = "vosk-model-small-es-0.42.zip"
MODEL_DIR = "vosk-model-small-es-0.42"

def download_file(url, filename):
    print(f"Downloading {url}...")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get('content-length', 0))
        dl = 0
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(50 * dl / total_length)
                    sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {dl/1024/1024:.2f} MB")
                    sys.stdout.flush()
    print("\nDownload complete.")

def extract_zip(zip_file, extract_to):
    print(f"Extracting {zip_file}...")
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")

def main():
    if os.path.exists(MODEL_DIR):
        print(f"Model directory '{MODEL_DIR}' already exists. Skipping download.")
        return

    if not os.path.exists(MODEL_ZIP):
        try:
            download_file(MODEL_URL, MODEL_ZIP)
        except Exception as e:
            print(f"Failed to download model: {e}")
            print("Please download it manually from:", MODEL_URL)
            return

    try:
        extract_zip(MODEL_ZIP, ".")
        # Rename to just 'model' for simpler access if preferred, strictly keeping it original name for now to match plan
    except Exception as e:
        print(f"Failed to extract zip: {e}")

    # clean up zip
    if os.path.exists(MODEL_ZIP):
        os.remove(MODEL_ZIP)
        print("Removed zip file.")

if __name__ == "__main__":
    main()
