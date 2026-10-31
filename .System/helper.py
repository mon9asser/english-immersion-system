
import subprocess
import tempfile
import helper
import re
import yt_dlp
from pathlib import Path
from faster_whisper import WhisperModel 
import pandas as pd 

file = Path("Usage.md")
_VIDEOS_FILE_DIR = Path("Videos.md")

TOTAL_COLUMNS = 8

names = [
    "Expressions",
    "Idioms",
    "Vocabularies"
]
DIR__ = "./Stories"
columns = ["No.", "Word / Expression"] + [str(i) for i in range(1, TOTAL_COLUMNS + 1)]

MEDIA_OUTPUT_DIR = Path("Media")

WHISPER_MODEL = "small"


def get_next_video_folder():
    MEDIA_OUTPUT_DIR.mkdir(exist_ok=True)

    existing = [
        int(folder.name.split("-")[1])
        for folder in MEDIA_OUTPUT_DIR.iterdir()
        if folder.is_dir()
        and folder.name.startswith("video-")
        and folder.name.split("-")[1].isdigit()
    ]

    next_number = max(existing, default=0) + 1

    folder = MEDIA_OUTPUT_DIR / f"video-{next_number}"
    folder.mkdir()

    return folder


def download_video(url, temp_dir):
    options = {
       "format": (
            "bestvideo[height<=720][vcodec^=avc1]+bestaudio[ext=m4a]"
            "/best[height<=720][ext=mp4]"
            "/bestvideo[height<=720]+bestaudio/best[height<=720]"
        ),
        "outtmpl": str(temp_dir / "source.%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": False,
        "noplaylist": True,
        "socket_timeout": 60,
        "retries": 20,
        "fragment_retries": 20,
        "extractor_retries": 5,
        "continuedl": True,
        "concurrent_fragment_downloads": 1,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=True)

    video_files = list(temp_dir.glob("source.*"))

    video_files = [
        file for file in video_files
        if file.suffix.lower() in {
            ".mp4", ".mkv", ".webm", ".mov"
        }
    ]

    if not video_files:
        raise FileNotFoundError("Downloaded video not found.")

    return video_files[0], info["duration"]


def split_video(video_path, output_folder, duration, interval):
    total_parts = (int(duration) + interval - 1) // interval

    print(f"\nSplitting video into {total_parts} parts...")

    for part_number in range(1, total_parts + 1):
        start = (part_number - 1) * interval
        part_duration = min(interval, duration - start)

        output_file = output_folder / f"part-{part_number}.mp4"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss", str(start),
                "-i", str(video_path),
                "-t", str(part_duration),
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-crf", "23",
                "-c:a", "aac",
                str(output_file),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"Created: {output_file.name}")


def create_transcripts(video_path, output_folder, duration, interval):
    print("\nGenerating transcript using Whisper...")

    model = WhisperModel(
        WHISPER_MODEL,
        device="cpu",
        compute_type="int8",
    )

    segments, info = model.transcribe(
        str(video_path),
        beam_size=5,
    )

    segments = list(segments)

    total_parts = (int(duration) + interval - 1) // interval
    transcripts = []

    for part_number in range(1, total_parts + 1):
        start = (part_number - 1) * interval
        end = min(start + interval, duration)

        transcript_file = (
            output_folder / f"transcript-{part_number}.txt"
        )

        lines = []

        for segment in segments:
            midpoint = (segment.start + segment.end) / 2

            if start <= midpoint < end:
                lines.append(segment.text.strip())

        transcript_text = " ".join(lines)

        transcripts.append(transcript_text)

        transcript_file.write_text(
            transcript_text,
            encoding="utf-8",
        )

        print(f"Created: {transcript_file.name}")

    return transcripts


def download(video_url, minutes):
    print("=== YouTube Video Splitter ===\n")

    url = video_url.strip()

    try:
        interval = int(
            minutes
        )

        if interval <= 0:
            raise ValueError

    except ValueError:
        print("Please enter a positive whole number.")
        return

    interval_seconds = interval * 60 

    try:
        with tempfile.TemporaryDirectory() as temp:
            temp_dir = Path(temp)

            print("\nDownloading video...")

            video_path, duration = download_video(
                url,
                temp_dir,
            )

            output_folder = get_next_video_folder()
            print(f"\nOutput folder: {output_folder}")

            print(
                f"\nVideo duration: "
                f"{duration / 60:.2f} minutes"
            )

            split_video(
                video_path,
                output_folder,
                duration,
                interval_seconds,
            )

            txt_transcript = create_transcripts(
                video_path,
                output_folder,
                duration,
                interval_seconds,
            )

            story_content = generate_story("\n".join(txt_transcript))

            create_story(video_url, story_content)

        print("\nAll done!")
        print(f"Files saved in: {output_folder}")

    except Exception as error:
        print(f"\nError: {error}")

 
def generate_story(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    paragraphs = []
    paragraph_size = 5  # Sentences per paragraph

    for i in range(0, len(sentences), paragraph_size):
        paragraph = " ".join(sentences[i:i + paragraph_size])
        paragraphs.append(paragraph)

    formatted_text = "\n\n".join(paragraphs) 

    return formatted_text

def extractor(file, col=0):

    file = Path(file)

    if not file.exists() or not file.is_file() or file.stat().st_size == 0:
        return []

    try:
        df = pd.read_csv(
            file,
            sep="|",
            skipinitialspace=True,
            skiprows=2,
            engine="python",
            on_bad_lines="skip"
        )

        df = df.dropna(axis=1, how="all")

        if df.empty or col >= len(df.columns):
            return []

        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        return [
            x for x in df.iloc[:, col].dropna().tolist()
            if isinstance(x, str) and not x.startswith("---")
        ]

    except pd.errors.EmptyDataError:
        return []


def scan(slug='Story-'):
    return [
        folder for folder in Path(DIR__).iterdir()
        if folder.is_dir() and folder.name.startswith(slug)
    ]

 
def scan_videos(file=''):
    file_dir = file if file != '' else _VIDEOS_FILE_DIR

    with open(file_dir, 'r', encoding='utf-8') as f:
        content = f.read()

    urls = re.findall(
        r'https?://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+)[^\s)]*',
        content
    )

    return urls
    
def read_speech():

    if not file.exists() or file.stat().st_size == 0:
        return pd.DataFrame(columns=columns)

    df = pd.read_csv(
        file,
        sep="|",
        skipinitialspace=True,
        engine="python"
    )

    df = df.dropna(axis=1, how="all")
    df.columns = df.columns.str.strip()
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # Remove Markdown separator rows
    df = df[
        ~df.iloc[:, 0].astype(str).str.startswith("---")
    ]

    return df


def update_speech():

    df = read_speech()

    # Collect existing words
    existing = set(df["Word / Expression"].dropna().tolist())

    new_words = []

    # Scan Video folders
    for folder in scan():

        for name in names:

            path = folder / f"{name}.md"
            
            vocab = extractor(path)

            for word in vocab:

                if word not in existing:
                    new_words.append(word)
                    existing.add(word)

    # Add new words with six unchecked boxes
    start = len(df) + 1

    new_rows = pd.DataFrame(
        [
            [start + i, word] + [" "] * TOTAL_COLUMNS
            for i, word in enumerate(new_words)
        ],
        columns=columns
    )

    df = pd.concat([df, new_rows], ignore_index=True)

    # Save Markdown table
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"

    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]

    content = "\n".join([header, separator] + rows)

    file.write_text(content, encoding="utf-8")

    print(f"Added {len(new_words)} new words.")
    print(f"Total words: {len(df)}")

def create_story(url, content='', directory=helper.DIR__):

    # Main directory
    main_dir = Path(directory)

    # Create main directory if it doesn't exist
    main_dir.mkdir(parents=True, exist_ok=True)

    # Get existing Story folders
    stories = []

    for folder in main_dir.iterdir():
        if folder.is_dir():
            match = re.fullmatch(r"Story-(\d+)", folder.name)

            if match:
                stories.append(int(match.group(1)))

    # Determine next story number
    next_number = max(stories, default=0) + 1

    # Create new story directory
    story_dir = main_dir / f"Story-{next_number}"
    story_dir.mkdir()

    # Files to create
    files = [
        "Expressions.md",
        "Grammar.md",
        "Idioms.md",
        "Listening.md",
        "Vocabularies.md",
        "Reading.md"
    ]

    # Create files
    for filename in files:

        file_path = story_dir / filename

        if filename == "Listening.md":
            file_path.write_text(url + "\n", encoding="utf-8")
        elif filename == "Reading.md":
            file_path.write_text(content + "\n", encoding="utf-8")
        else:
            file_path.touch()

    print(f"Created: {story_dir}")

    return story_dir

