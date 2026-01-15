# Podcast Transcripts - Checking In by Hotel Owner

Automated transcription system for "Checking In by Hotel Owner" podcast episodes using AssemblyAI API. Currently contains 8 transcribed episodes focused on guest experience, customer insights, and hospitality innovation.

## What's Included

**8 Episodes (~6 hours total):**
1. **Francisco Macedo** - Innovation & redefining hospitality (48 min) - HIGH insights
2. **Mike Baxter** - House of Gods guest experience & brand identity (49 min) - HIGH insights
3. **Olivia Immesi** - Native Places sustainability & inclusivity (58 min) - HIGH insights
4. **Ian Taylor** - Kaleidoscope design-led hotels (44 min) - HIGH insights
5. **Anna Corkill** - Hyatt UK expansion & market trends (29 min)
6. **Karim Kassam** - Horwood House leadership & culture (67 min)
7. **Pierre Deburaux** - Accor people-first approach (34 min)
8. **Natalia Dainty** - Learning & staff development (44 min)

**Each episode has:**
- Full transcript with speaker identification
- Auto-generated chapter summaries with timestamps
- Both JSON (full metadata) and Markdown (readable) formats
- Confidence scores and audio duration

## Files

```
├── episodes.json              # Episode metadata with audio URLs
├── transcribe-with-api.py     # Python transcription script
└── transcripts/               # Generated transcripts (16 files)
    ├── ep47-francisco-macedo-innovation.json
    ├── ep47-francisco-macedo-innovation.md
    └── ... (8 episodes × 2 formats)
```

## How to Transcribe New Episodes

**1. Install dependencies (one-time):**
```bash
pip3 install --break-system-packages assemblyai
```

**2. Get API key:**
- Sign up at [assemblyai.com](https://www.assemblyai.com/)
- Free tier: $50 credit (enough for ~185 hours)
- Cost: ~$0.25 per hour of audio

**3. Add new episodes to `episodes.json`:**
```json
{
  "id": 9,
  "title": "Episode Title",
  "guest": "Guest Name, Title",
  "date": "2025-01-15",
  "duration": "45:00",
  "audio_url": "https://direct-audio-url.mp3",
  "filename": "ep##-guest-name-topic.mp3",
  "focus": "Main topics covered",
  "customer_insights": "high|medium|low"
}
```

**4. Run transcription:**
```bash
export ASSEMBLYAI_API_KEY="your-api-key-here"
python3 transcribe-with-api.py
```

**Script features:**
- Skips already-transcribed episodes automatically
- Processes one episode at a time
- Takes ~5-7 minutes per episode
- Creates both JSON and Markdown files
- No audio files saved locally (transcribes from URLs)

## Transcript Formats

### JSON Format
Contains complete metadata:
- Episode information (guest, date, duration, focus)
- Full transcript text with word count and confidence
- Speaker-by-speaker utterances with timestamps
- Chapter summaries with headlines and gists
- Start/end times for all segments

### Markdown Format
Human-readable format with:
- Episode header (guest, date, duration, focus)
- Transcription confidence score
- Chapter summaries with timestamps
- Full transcript with speaker labels and timestamps

## Usage for Signals Demo

Upload either format (JSON or Markdown) to Signals. The transcripts provide rich hospitality industry insights from operators discussing:
- What they believe customers value
- Market trends and positioning strategies
- How staff culture affects guest experience
- Innovation in guest experience design
