
import pandas as pd
from pathlib import Path

file = Path("Speech.md")
TOTAL_COLUMNS = 8

names = [
    "Expressions",
    "Idioms",
    "Vocabularies"
]

columns = ["No.", "Word / Expression"] + [str(i) for i in range(1, TOTAL_COLUMNS + 1)]


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


def scan():
    return [
        folder for folder in Path(".").iterdir()
        if folder.is_dir() and folder.name.startswith("Story-")
    ]


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

    # Scan story folders
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


update_speech()
