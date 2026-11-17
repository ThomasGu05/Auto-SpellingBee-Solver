import urllib.request
import json
import re
from pathlib import Path

SCRABBLE_WORDS = []
with Path(__file__).with_name("sowpods.txt").open() as f:
    for line in f:
        SCRABBLE_WORDS.append(line.strip().upper())


def validate_word(required_letter: str, all_letters: str, word: str):
    '''
    The function determines if word is a valid word
    words that score 0 are "invalid" words -- see score rules above
    returns True for valid words otherwise False
    '''

    if not isinstance(word, str):
        return False

    word = word.strip()

    if len(word) < 4:
        return False

    for alp in word:
        if alp not in all_letters:
            return False
    if required_letter not in word:
        return False

    return True


def score_word(required_letter, all_letters, word):
    """
    Takes 3 string parameters: required_letter, all_letters, and word and calculates how many points it would earn based on the Scoring rules.
    """
    if not validate_word(required_letter, all_letters, word):
        return 0

    if len(word) == 4:
        score = 1
    else:
        score = len(word)

    s = len(all_letters)
    for a in all_letters:
        if a in word:
            s -= 1
    if s < 1:
        score += 7

    return score


def spelling_bee(required_letter, all_letters):
    scores = []
    for word in SCRABBLE_WORDS:
        if score_word(required_letter, all_letters, word) > 0:
            scores.append((score_word(required_letter, all_letters, word), word))
    return sorted(scores)[::-1]

def fetch_nyt_letters():
    url = "https://www.nytimes.com/puzzles/spelling-bee"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "SpellingBeeSolver/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8")

    match = re.search(r"window\.gameData\s*=\s*", html)

    if match is None:
        raise ValueError("Couldn't find game data.")

    remaining = html[match.end():].lstrip()
    game_data, _ = json.JSONDecoder().raw_decode(remaining)

    today = game_data["today"]
    required_letter = today["centerLetter"].upper()
    all_letters = "".join(today["validLetters"]).upper()
    answers = [word.upper() for word in today["answers"]]

    return required_letter, all_letters, answers

try:
    required_letter, all_letters, answers = fetch_nyt_letters()

    print("Required Letter:", required_letter)
    print("All Letters:", all_letters)

    results = []

    for word in answers:
        score = score_word(required_letter, all_letters, word)
        results.append((score, word))

    results.sort(reverse=True)

    for score, word in results:
        print(word, score)

    print("NYT Answer Count:", len(results))
    print("NYT Maximum Score:", sum(score for score, word in results))

except Exception as error:
    print("Could not fetch data:", error)

input("\nPress enter to exit...")