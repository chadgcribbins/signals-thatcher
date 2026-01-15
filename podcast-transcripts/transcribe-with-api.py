#!/usr/bin/env python3
"""
Transcribe "Checking In by Hotel Owner" podcast episodes using AssemblyAI
No audio download required - transcribes directly from URLs
"""

import json
import os
import time
from pathlib import Path

try:
    import assemblyai as aai
except ImportError:
    print("❌ AssemblyAI not installed")
    print("\nInstall with: pip install assemblyai")
    print("\nThen get a free API key at: https://www.assemblyai.com/")
    exit(1)

# Configuration
SCRIPT_DIR = Path(__file__).parent
EPISODES_JSON = SCRIPT_DIR / "episodes.json"
TRANSCRIPT_DIR = SCRIPT_DIR / "transcripts"
TRANSCRIPT_DIR.mkdir(exist_ok=True)

# Get API key from environment
API_KEY = os.environ.get("ASSEMBLYAI_API_KEY")
if not API_KEY:
    print("❌ ASSEMBLYAI_API_KEY environment variable not set")
    print("\nGet a free API key at: https://www.assemblyai.com/")
    print("Then run: export ASSEMBLYAI_API_KEY='your-key-here'")
    exit(1)

aai.settings.api_key = API_KEY

def load_episodes():
    """Load episode metadata from JSON"""
    with open(EPISODES_JSON, 'r') as f:
        data = json.load(f)
    return data['episodes']

def transcribe_episode(episode):
    """Transcribe a single episode using AssemblyAI"""

    filename_base = Path(episode['filename']).stem
    json_output = TRANSCRIPT_DIR / f"{filename_base}.json"
    md_output = TRANSCRIPT_DIR / f"{filename_base}.md"

    # Skip if already transcribed
    if json_output.exists() and md_output.exists():
        print(f"✓ Already transcribed: {episode['title'][:50]}...")
        return True

    print(f"\n🎧 Transcribing: {episode['title']}")
    print(f"   Guest: {episode['guest']}")
    print(f"   Duration: {episode['duration']}")

    try:
        # Configure transcription
        config = aai.TranscriptionConfig(
            speaker_labels=True,  # Identify different speakers
            auto_chapters=True,   # Generate chapter summaries
            entity_detection=True, # Detect named entities
            sentiment_analysis=True # Analyze sentiment
        )

        # Start transcription
        transcriber = aai.Transcriber()
        print("   ⏳ Uploading and processing audio...")
        transcript = transcriber.transcribe(episode['audio_url'], config)

        # Wait for completion
        while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
            time.sleep(3)
            print("   ⏳ Still processing...")

        if transcript.status == aai.TranscriptStatus.error:
            print(f"   ❌ Error: {transcript.error}")
            return False

        # Save JSON with full metadata
        transcript_data = {
            "episode": {
                "title": episode['title'],
                "guest": episode['guest'],
                "date": episode['date'],
                "duration": episode['duration'],
                "focus": episode['focus']
            },
            "transcription": {
                "text": transcript.text,
                "words": len(transcript.text.split()),
                "confidence": transcript.confidence,
                "audio_duration": transcript.audio_duration
            },
            "utterances": [
                {
                    "speaker": u.speaker,
                    "text": u.text,
                    "start": u.start,
                    "end": u.end,
                    "confidence": u.confidence
                }
                for u in transcript.utterances
            ] if transcript.utterances else [],
            "chapters": [
                {
                    "summary": chapter.summary,
                    "gist": chapter.gist,
                    "headline": chapter.headline,
                    "start": chapter.start,
                    "end": chapter.end
                }
                for chapter in transcript.chapters
            ] if transcript.chapters else []
        }

        with open(json_output, 'w') as f:
            json.dump(transcript_data, f, indent=2)

        # Create readable Markdown
        md_content = f"""# {episode['title']}

**Guest:** {episode['guest']}
**Date:** {episode['date']}
**Duration:** {episode['duration']}
**Focus:** {episode['focus']}

**Transcription Confidence:** {transcript.confidence:.2%}
**Audio Duration:** {transcript.audio_duration/1000:.1f} seconds

---

## Summary

{transcript.chapters[0].summary if transcript.chapters else "No summary available"}

---

## Chapters
"""

        if transcript.chapters:
            for i, chapter in enumerate(transcript.chapters, 1):
                timestamp = f"{chapter.start//60000}:{(chapter.start//1000)%60:02d}"
                md_content += f"\n### {i}. {chapter.headline} ({timestamp})\n\n"
                md_content += f"{chapter.summary}\n\n"

        md_content += "\n---\n\n## Full Transcript\n\n"

        if transcript.utterances:
            for u in transcript.utterances:
                timestamp = f"{u.start//60000}:{(u.start//1000)%60:02d}"
                md_content += f"**{u.speaker}** ({timestamp}): {u.text}\n\n"
        else:
            md_content += transcript.text

        with open(md_output, 'w') as f:
            f.write(md_content)

        print(f"   ✓ Saved: {json_output.name}")
        print(f"   ✓ Saved: {md_output.name}")
        return True

    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("🎙️  Podcast Transcript Generator")
    print("=" * 60)
    print()

    episodes = load_episodes()
    print(f"Found {len(episodes)} episodes to transcribe")
    print()

    success_count = 0
    for i, episode in enumerate(episodes, 1):
        print(f"[{i}/{len(episodes)}]", end=" ")
        if transcribe_episode(episode):
            success_count += 1

    print()
    print("=" * 60)
    print(f"✅ Complete! Transcribed {success_count}/{len(episodes)} episodes")
    print()
    print(f"Transcripts saved to: {TRANSCRIPT_DIR}")
    print()
    print("You can now upload these files to Signals!")

if __name__ == "__main__":
    main()
