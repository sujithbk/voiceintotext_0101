import json
from getpass import getpass
from pathlib import Path
from sarvamai import SarvamAI

folder = Path(__file__).resolve().parent
audio = folder / "voiceq.mp3"

if not audio.exists():
    raise SystemExit("Place voiceq.mp3 beside this script.")

client = SarvamAI(
    api_subscription_key=getpass("Enter your Sarvam API key: ")
)

job = client.speech_to_text_job.create_job(
    model="saaras:v4",
    mode="transcribe",
)

job.upload_files(file_paths=[str(audio)])
job.start()
print("Transcribing...")
job.wait_until_complete()

results = job.get_file_results()
if results["failed"]:
    raise SystemExit(str(results["failed"]))

output = folder / "sarvam_output"
job.download_outputs(output_dir=str(output))

transcripts = []
for file in sorted(output.rglob("*.json")):
    data = json.loads(file.read_text(encoding="utf-8"))
    if data.get("transcript"):
        transcripts.append(data["transcript"])

if not transcripts:
    raise SystemExit("Check sarvam_output for the returned results.")

text = "\n\n".join(transcripts)
(folder / "transcript.txt").write_text(text, encoding="utf-8")
print(text)
print("\nSaved to transcript.txt")