"""Download pretrained models needed by GPT-SoVITS TTS."""
import os
import sys
from huggingface_hub import snapshot_download, hf_hub_download

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRETRAINED_DIR = os.path.join(BASE_DIR, "GPT_SoVITS", "pretrained_models")


def download_bert():
    path = os.path.join(PRETRAINED_DIR, "chinese-roberta-wwm-ext-large")
    if os.path.exists(path):
        print(f"[SKIP] {path} already exists")
        return
    print("[1/4] Downloading chinese-roberta-wwm-ext-large...")
    snapshot_download(
        repo_id="hfl/chinese-roberta-wwm-ext-large",
        local_dir=path,
        local_dir_use_symlinks=False,
    )
    print("  Done.")


def download_hubert():
    path = os.path.join(PRETRAINED_DIR, "chinese-hubert-base")
    if os.path.exists(path):
        print(f"[SKIP] {path} already exists")
        return
    print("[2/4] Downloading chinese-hubert-base...")
    snapshot_download(
        repo_id="TencentGameMate/chinese-hubert-base",
        local_dir=path,
        local_dir_use_symlinks=False,
    )
    print("  Done.")


def download_gpt_sovits_v2():
    save_dir = os.path.join(PRETRAINED_DIR, "gsv-v2final-pretrained")
    os.makedirs(save_dir, exist_ok=True)

    files = {
        "s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt": "gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt",
        "s2G2333k.pth": "gsv-v2final-pretrained/s2G2333k.pth",
    }

    for fname, repo_path in files.items():
        dest = os.path.join(save_dir, fname)
        if os.path.exists(dest):
            print(f"[SKIP] {fname} already exists")
            continue
        print(f"[3/4] Downloading {fname}...")
        hf_hub_download(
            repo_id="lj1995/GPT-SoVITS",
            subfolder="gsv-v2final-pretrained",
            filename=fname,
            local_dir=PRETRAINED_DIR,
            local_dir_use_symlinks=False,
        )
        print("  Done.")


def download_gpt_sovits_v1():
    save_dir = PRETRAINED_DIR
    files = {
        "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt": "s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt",
        "s2G488k.pth": "s2G488k.pth",
    }

    for fname, repo_path in files.items():
        dest = os.path.join(save_dir, fname)
        if os.path.exists(dest):
            print(f"[SKIP] {fname} already exists")
            continue
        print(f"[4/4] Downloading {fname}...")
        hf_hub_download(
            repo_id="lj1995/GPT-SoVITS",
            filename=fname,
            local_dir=PRETRAINED_DIR,
            local_dir_use_symlinks=False,
        )
        print("  Done.")


if __name__ == "__main__":
    download_bert()
    download_hubert()
    download_gpt_sovits_v2()
    download_gpt_sovits_v1()
    print("\nAll models downloaded to:", PRETRAINED_DIR)
