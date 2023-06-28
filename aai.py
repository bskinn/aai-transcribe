# pip install requests tqdm black
# Store your AssemblyAI token in env var AAI_TOKEN
import itertools as itt
import json
import os
import sys
import time
from pathlib import Path

import requests as rq
from tqdm import tqdm

BASE_URL = "https://api.assemblyai.com/v2"

UTTERANCE_FORMAT = "[[{speaker}]] ({timestamp}): {text}\n\n"


def make_timestamp(milliseconds):
    seconds = milliseconds // 1000

    seconds -= (hours := seconds // 3600) * 3600
    seconds -= (minutes := seconds // 60) * 60

    return (
        f"{hours}:{minutes:>02}:{seconds:>02}"
        if hours
        else f"{minutes:>02}:{seconds:>02}"
    )


def main():
    if len(sys.argv) != 2:
        print("Need filename as CLI arg!")
        return 1

    headers = {"authorization": os.getenv("AAI_TOKEN")}

    print("Attempting audio upload...", end="")
    try:
        with open(sys.argv[1], "rb") as f:
            resp_upload = rq.post(BASE_URL + "/upload", headers=headers, data=f)
    except Exception as e:
        print(f"Audio upload failed:\n\n{e}")
        return 1
    print("Done!")

    upload_url = resp_upload.json()["upload_url"]

    payload = {
        "audio_url": upload_url,
        "speaker_labels": True,
    }

    print("Attempting to submit transcription request...", end="")
    try:
        resp_transcribe = rq.post(
            BASE_URL + "/transcript", json=payload, headers=headers
        )
    except Exception as e:
        print(f"Transcription request failed:\\n{e}")
        return 1
    print("Done!")

    transcript_id = resp_transcribe.json()["id"]
    polling_endpoint = f"{BASE_URL}/transcript/{transcript_id}"

    print("Awaiting transcription:")
    for _ in tqdm(itt.count()):
        resp_result = rq.get(polling_endpoint, headers=headers)
        json_result = resp_result.json()

        if json_result["status"] == "completed":
            print("\n\nDone!")

            Path("transcript_raw.txt").write_text(json_result["text"])
            Path("utterances.json").write_text(json.dumps(json_result["utterances"]))

            text_split = ""
            for u in json_result["utterances"]:
                text_split += UTTERANCE_FORMAT.format(
                    speaker=u["speaker"],
                    timestamp=make_timestamp(u["start"]),
                    text=u["text"],
                )

            Path("transcript_split.txt").write_text(text_split)
            return 0

        elif json_result["status"] == "error":
            print(f"Transcription failed:\n\n{json_result['error']}")
            return 1

        else:
            time.sleep(3)


if __name__ == "__main__":
    sys.exit(main())
