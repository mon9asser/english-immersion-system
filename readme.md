# English Learning Tools

A collection of Python scripts designed to help organize English-learning materials from YouTube videos.

The project provides three main tools:

1. Download and split all videos in a predefined list.
2. Download and split a single YouTube video.
3. Extract useful English-learning content from transcripts.

## Project Structure

```text
english/
├── code/
│   ├── download_all.py
│   ├── download_video.py
│   ├── words.py
│   └── helper.py
├── videos/
│   └── ...
└── README.md
```

## Requirements

- Python 3.11+
- FFmpeg
- Required Python packages

Activate the virtual environment before running the scripts:

```bash
source .venv311/bin/activate
```

## 1. Download All Videos

**File:** `code/download_all.py`

Downloads all videos from the predefined video list and splits each video into smaller segments.

When you run the script, it asks you to enter the number of minutes for each segment.

**Run:**

```bash
python code/download_all.py
```

**Example:**

```text
Enter the number of minutes to split videos into: 3
```

Each video will be downloaded and divided into segments of approximately 3 minutes.

## 2. Download a Single Video

**File:** `code/download_video.py`

Downloads one YouTube video and splits it into smaller segments.

Unlike `download_all.py`, this script asks you to provide the YouTube URL manually.

**Run:**

```bash
python code/download_video.py
```

**Example:**

```text
Enter YouTube video URL: https://www.youtube.com/watch?v=VIDEO_ID
Enter the number of minutes for each segment: 3
```

The script downloads the specified video and splits it into segments based on your chosen duration.

## 3. Extract English Learning Content

**File:** `code/words.py`

Extracts useful English-learning content from speech transcripts and organizes it into a Markdown file named `speech.md`.

The extracted content includes:

- **Idioms:** Common English idiomatic expressions and their meanings.
- **Vocabulary:** Useful words and their meanings.
- **Sentences:** Important sentences from the speech.
- **Expressions:** Common phrases and expressions used by the speaker.

The generated `speech.md` file provides organized learning material that you can review and study.

**Run:**

```bash
python code/words.py
```

## Recommended Workflow

1. Use `download_all.py` to process your predefined collection of videos.
2. Use `download_video.py` when you want to study a specific YouTube video.
3. Use `words.py` to extract useful English-learning content into `speech.md`.
4. Review the extracted vocabulary, idioms, sentences, and expressions.
5. Practice listening, shadowing, speaking, and writing using the downloaded video segments.

## Purpose

The goal of this project is to turn English videos into organized learning materials, making it easier to practice listening, improve pronunciation, expand vocabulary, and learn natural English expressions.