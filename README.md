# aai-transcribe

Helper repo for submitting an audio file to AssemblyAI for
diarized transcription.

**NOTE:** I don't have any plans for further development on this,
or to keep it updated as Python and the AssemblyAI API evolves,
so I'm archiving it.

## Setup

Clone the repo:

```
$ git clone https://github.com/bskinn/aai-transcribe
```

Enter the cloned repo directory, create and activate a Python 3.11+ virtualenv.

Update `pip`:

```
(env) $ python -m pip install -U pip
```

Install dependencies:

```
(env) $ python -m pip install -r requirements.txt
```

Obtain an AssemblyAI API token and store it as the `AAI_TOKEN`
environment variable.


## Transcription

Activate the virtual environment and pass the path to the audio file to be
transcribed into the `aai.py` script:

```
(env) $ python aai.py {path to audio file}
```

The script will handle the initial submission to AssemblyAI, followed by
the request for diarized transcription. It then polls the AssemblyAI
status endpoint until transcription has completed, then downloads the
resulting transcript JSON payload as `utterances.json`.

It then produces two files:

- `transcript_raw.txt` -- The transcript without diarization
- `transcript_split.txt` -- The transcript with diarization

AssemblyAI does not have access to the names of the speakers, so the script outputs
anonymized labels for the transcription instead (e.g., `[[A]]` and `[[B]]`). It's thus
necessary to manually do a find-and-replace to swap in each speaker's name in place
of their name placeholder.

The speaker identification is usually fairly reliable with two or three unique speakers.
With larger groups, inaccuracies are common. Manual cross-checking of all speaker names
is a good idea.
