"""
data_analysis_M3.py

Analysis module for the MATH1604 group project.

This module is responsible for processing the collated quiz answer data,
computing the mean answer value for each question, and producing simple
visualisations that help investigate possible answer patterns.

Team Member 3 (M3) functions:
    - generate_means_sequence(collated_answers_path)
    - visualize_data(collated_answers_path, n)
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Iterable, List

import matplotlib.pyplot as plt


NUMBER_OF_QUESTIONS = 100
VALID_ANSWERS = {0, 1, 2, 3, 4}


def _parse_raw_question_section(section_text: str) -> list[int] | None:
    """
    Parse one raw respondent section written in the original quiz text format.

    This helper is included to make the analysis module more robust if the
    collated file contains raw respondent text rather than already-extracted
    answer sequences.

    Parameters
    ----------
    section_text : str
        Text for one respondent. It may contain lines such as
        ``Question 1. ...`` followed by answer options marked with ``[x]``
        or ``[ ]``.

    Returns
    -------
    list[int] | None
        A list of 100 integers if the raw format is detected and parsed
        successfully. Values are in ``{0, 1, 2, 3, 4}``, where 0 means
        unanswered. Returns ``None`` if the section does not look like raw
        quiz text.

    Raises
    ------
    ValueError
        If the section looks like raw quiz text but contains an invalid
        question structure, such as more than one selected answer for a
        question.
    """
    if "Question" not in section_text or "[" not in section_text:
        return None

    answers: list[int] = []
    selected_answer = 0
    option_number = 0
    inside_question = False
    selected_count = 0

    for line in section_text.splitlines():
        stripped = line.strip()

        if re.match(r"^Question\s+\d+\b", stripped, flags=re.IGNORECASE):
            if inside_question:
                answers.append(selected_answer)

            inside_question = True
            selected_answer = 0
            option_number = 0
            selected_count = 0
            continue

        if inside_question:
            option_match = re.match(r"^\[\s*([xX]?)\s*\]", stripped)
            if option_match:
                option_number += 1
                mark = option_match.group(1).lower()

                if mark == "x":
                    selected_count += 1
                    if selected_count > 1:
                        raise ValueError(
                            "Invalid raw quiz section: more than one selected "
                            "answer was found for one question."
                        )
                    selected_answer = option_number

    if inside_question:
        answers.append(selected_answer)

    if len(answers) == NUMBER_OF_QUESTIONS:
        return answers

    # If it only contains a small example or a different text block, do not
    # force raw parsing. The numeric parser may still handle it.
    return None


def _parse_numeric_section(section_text: str) -> list[int]:
    """
    Parse one respondent section that contains an extracted numeric sequence.

    The function accepts common sequence formats, for example:
    ``1 2 0 4 ...``, ``1,2,0,4,...`` or ``[1, 2, 0, 4, ...]``.
    It also ignores simple labels such as ``Respondent 1:``.

    Parameters
    ----------
    section_text : str
        Text for one respondent answer sequence.

    Returns
    -------
    list[int]
        A list of 100 integers in ``{0, 1, 2, 3, 4}``.

    Raises
    ------
    ValueError
        If the section does not contain exactly 100 valid answer values.
    """
    useful_lines: list[str] = []

    for line in section_text.splitlines():
        stripped = line.strip()

        if not stripped or stripped == "*":
            continue

        # Remove common respondent labels before checking whether the line is
        # a numeric answer sequence.
        stripped = re.sub(
            r"^\s*(respondent|answers_respondent|answer_sequence|sequence)"
            r"\s*_?\s*\d+\s*[:=\-]?\s*",
            "",
            stripped,
            flags=re.IGNORECASE,
        )

        # Keep only lines that look like answer sequences. This prevents
        # accidental parsing of words, question numbers, or explanatory text.
        if re.fullmatch(r"[\[\]\(\)\{\}\s,;0-4]+", stripped):
            useful_lines.append(stripped)

    search_text = " ".join(useful_lines) if useful_lines else section_text
    values = [int(token) for token in re.findall(r"(?<!\d)[0-4](?!\d)", search_text)]

    if len(values) != NUMBER_OF_QUESTIONS:
        raise ValueError(
            f"Expected {NUMBER_OF_QUESTIONS} answer values for one respondent, "
            f"but found {len(values)}. Please check the collated file format."
        )

    if any(value not in VALID_ANSWERS for value in values):
        raise ValueError("Answer values must be 0, 1, 2, 3, or 4 only.")

    return values


def _read_collated_answers(collated_answers_path: str | Path) -> list[list[int]]:
    """
    Read a collated answer file and return respondent answer sequences.

    The expected project format is a collated text file containing one
    respondent answer sequence per section. Sections may be separated by a
    line containing ``*``. Each respondent sequence must contain 100 values.

    This helper also supports a fallback format where the whole file contains
    several 100-value numeric sequences without explicit ``*`` separators.

    Parameters
    ----------
    collated_answers_path : str or pathlib.Path
        Path to the collated answers file, usually
        ``output/collated_answers.txt``.

    Returns
    -------
    list[list[int]]
        A list where each inner list contains the 100 answers for one
        respondent.

    Raises
    ------
    FileNotFoundError
        If ``collated_answers_path`` does not exist.
    ValueError
        If no valid respondent sequences can be parsed from the file.
    """
    path = Path(collated_answers_path)

    if not path.exists():
        raise FileNotFoundError(f"Collated answers file not found: {path}")

    text = path.read_text(encoding="utf-8", errors="replace")

    if not text.strip():
        raise ValueError("The collated answers file is empty.")

    # Main expected format: respondent sections separated by a line containing *.
    sections = re.split(r"(?m)^\s*\*\s*$", text)
    respondent_sequences: list[list[int]] = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        raw_sequence = _parse_raw_question_section(section)
        if raw_sequence is not None:
            respondent_sequences.append(raw_sequence)
        else:
            respondent_sequences.append(_parse_numeric_section(section))

    # Fallback: if there were no useful sections, or if there is one large
    # numeric file without * separators, split values into chunks of 100.
    if len(respondent_sequences) == 1:
        try:
            values = [
                int(token)
                for token in re.findall(r"(?<!\d)[0-4](?!\d)", text)
            ]
            if len(values) > NUMBER_OF_QUESTIONS and len(values) % NUMBER_OF_QUESTIONS == 0:
                respondent_sequences = [
                    values[i : i + NUMBER_OF_QUESTIONS]
                    for i in range(0, len(values), NUMBER_OF_QUESTIONS)
                ]
        except ValueError:
            pass

    if not respondent_sequences:
        raise ValueError("No respondent answer sequences were found.")

    for row_number, answers in enumerate(respondent_sequences, start=1):
        if len(answers) != NUMBER_OF_QUESTIONS:
            raise ValueError(
                f"Respondent {row_number} has {len(answers)} values; "
                f"expected {NUMBER_OF_QUESTIONS}."
            )

    return respondent_sequences


def generate_means_sequence(collated_answers_path: str | Path) -> list[float]:
    """
    Return the mean answer value for each of the 100 quiz questions.

    For each question, the function computes the mean of the selected answer
    values across all respondents. Unanswered questions are coded as 0 and are
    excluded from the mean calculation, as required in the project brief.

    Parameters
    ----------
    collated_answers_path : str or pathlib.Path
        Path to the collated answers file. The usual project path is
        ``output/collated_answers.txt``.

    Returns
    -------
    list[float]
        A list of length 100. The value at index 0 is the mean answer value
        for Question 1, the value at index 1 is the mean for Question 2, and
        so on. If all respondents left a question unanswered, the mean for
        that question is returned as ``math.nan`` because no valid non-zero
        answer exists.

    Raises
    ------
    FileNotFoundError
        If the collated answers file cannot be found.
    ValueError
        If the file cannot be parsed into valid 100-value respondent
        sequences.
    """
    respondent_sequences = _read_collated_answers(collated_answers_path)

    means: list[float] = []

    for question_index in range(NUMBER_OF_QUESTIONS):
        answered_values = [
            respondent[question_index]
            for respondent in respondent_sequences
            if respondent[question_index] != 0
        ]

        if answered_values:
            means.append(sum(answered_values) / len(answered_values))
        else:
            means.append(math.nan)

    return means


def visualize_data(collated_answers_path: str | Path, n: int):
    """
    Visualise the mean answer value for each question.

    The function first calls ``generate_means_sequence`` and then plots the
    100 mean answer values against question number.

    Parameters
    ----------
    collated_answers_path : str or pathlib.Path
        Path to the collated answers file, usually
        ``output/collated_answers.txt``.
    n : int
        Plot type selector:
        - ``1`` creates a scatter plot.
        - ``2`` creates a line plot.
        Any other value prints an error message and returns ``None``.

    Returns
    -------
    tuple[matplotlib.figure.Figure, matplotlib.axes.Axes] | None
        The matplotlib figure and axes objects for the requested plot. Returns
        ``None`` if ``n`` is not 1 or 2.

    Raises
    ------
    FileNotFoundError
        If the collated answers file cannot be found.
    ValueError
        If the file format is invalid.
    """
    if n not in (1, 2):
        print("Error: n must be 1 for a scatter plot or 2 for a line plot.")
        return None

    means = generate_means_sequence(collated_answers_path)
    question_numbers = list(range(1, NUMBER_OF_QUESTIONS + 1))

    fig, ax = plt.subplots(figsize=(10, 5))

    if n == 1:
        ax.scatter(question_numbers, means)
        ax.set_title("Mean Answer Value by Question - Scatter Plot")
    else:
        ax.plot(question_numbers, means, marker="o", linewidth=1)
        ax.set_title("Mean Answer Value by Question - Line Plot")

    ax.set_xlabel("Question number")
    ax.set_ylabel("Mean answer value, excluding unanswered values")
    ax.set_xticks(range(0, NUMBER_OF_QUESTIONS + 1, 10))
    ax.set_yticks([1, 2, 3, 4])
    ax.set_ylim(0.8, 4.2)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    plt.show()

    return fig, ax


if __name__ == "__main__":
    # This small block is only for quick manual testing.
    # In the final project, M4 should call these functions from the full
    # analysis pipeline.
    default_path = Path("output") / "collated_answers.txt"

    if default_path.exists():
        print("First 10 mean values:")
        print(generate_means_sequence(default_path)[:10])
        visualize_data(default_path, 1)
        visualize_data(default_path, 2)
    else:
        print(
            "No output/collated_answers.txt file found. "
            "Run the full project pipeline or provide the collated file first."
        )

