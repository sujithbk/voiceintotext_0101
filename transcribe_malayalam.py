import json
import os
import sys
from getpass import getpass
from pathlib import Path
from dotenv import load_dotenv
from sarvamai import SarvamAI

folder = Path(__file__).resolve().parent
load_dotenv(folder / ".env")
audio = folder / (sys.argv[1] if len(sys.argv) > 1 else "Meet_audio.mp3")

if not audio.exists():
    raise SystemExit(f"Audio not found: {audio}")

client = SarvamAI(
    api_subscription_key=os.environ.get("SARVAM_API_KEY")
    or getpass("Enter your Sarvam API key: ")
)

job = client.speech_to_text_job.create_job(
    model="saaras:v4",
    mode="transcribe",
    language_code="ml-IN",
    with_diarization=True,
)

job.upload_files(file_paths=[str(audio)])
job.start()
print(f"Transcribing {audio.name} (Malayalam)...")
job.wait_until_complete()

results = job.get_file_results()
if results["failed"]:
    raise SystemExit(str(results["failed"]))

output = folder / "sarvam_output" / audio.stem
job.download_outputs(output_dir=str(output))

transcripts = []
for file in sorted(output.rglob("*.json")):
    data = json.loads(file.read_text(encoding="utf-8"))
    entries = (data.get("diarized_transcript") or {}).get("entries")
    if entries:
        transcripts.append("\n".join(
            f"Speaker {e.get('speaker_id')}: {e.get('transcript', '').strip()}"
            for e in entries
        ))
    elif data.get("transcript"):
        transcripts.append(data["transcript"])

if not transcripts:
    raise SystemExit(f"Check {output} for the returned results.")

text = "\n\n".join(transcripts)
target = folder / f"{audio.stem}_malayalam.txt"
target.write_text(text, encoding="utf-8")
print(text)
print(f"\nSaved to {target.name}")
