# ragebater input keyword analysis

QUESTION_STARTERS = (
    "what ",
    "why ",
    "how ",
    "when ",
    "where ",
    "who ",
    "can ",
    "could ",
    "would ",
    "is ",
    "are ",
    "do ",
    "does ",
)

GREETING_WORDS = {
    "hello",
    "hi",
    "hey",
    "yo",
    "sup",
}

COMMAND_STARTERS = (
    "do ",
    "make ",
    "create ",
    "show ",
    "tell me ",
    "explain ",
)

POSITIVE_WORDS = {
    "love",
    "great",
    "awesome",
    "good",
    "amazing",
    "nice",
}

NEGATIVE_WORDS = {
    "hate",
    "bad",
    "terrible",
    "stupid",
    "useless",
    "sucks",
}

FRUSTRATION_WORDS = {
    "frustrated",
    "annoying",
    "annoyed",
    "angry",
    "not working",
    "doesn't work",
    "doesnt work",
    "why isn't",
    "why isnt",
    "why doesn't",
    "why doesnt",
}

CONFIDENT_WORDS = {
    "obviously",
    "definitely",
    "clearly",
    "easy",
    "simple",
}

PLAYFUL_WORDS = {
    "lol",
    "lmao",
    "haha",
    "bro",
    "dude",
}

HOSTILE_WORDS = {
    "stupid",
    "idiot",
    "dumb",
    "useless",
    "trash",
    "sucks",
    "shut up",
    "moron",
    "loser",
}

TOPIC_KEYWORDS = {
    "python": ("python",),
    "javascript": ("javascript", "js"),
    "programming": (
        "programming",
        "program",
        "coding",
        "code",
        "developer",
        "development",
    ),
    "ai": (
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "llm",
    ),
    "robotics": (
        "robot",
        "robotics",
        "arduino",
        "raspberry pi",
    ),
    "gaming": (
        "game",
        "gaming",
        "gamer",
        "minecraft",
        "valorant",
        "fortnite",
    ),
    "school": (
        "school",
        "homework",
        "exam",
        "class",
        "assignment",
        "student",
    ),
}


def _normalize(message: str) -> str:
    """Normalize a message for deterministic matching."""
    return " ".join(message.strip().lower().split())


def _contains_any(text: str, words: set[str]) -> bool:
    """Return True when any keyword appears in the text."""
    return any(word in text for word in words)


def _detect_intent(message: str) -> tuple[str, float]:
    """Detect the primary intent and classification confidence."""
    text = _normalize(message)

    if not text:
        return "unknown", 0.0

    words = text.split()

    # A standalone greeting gets the strongest greeting classification.
    if len(words) <= 3 and any(word in GREETING_WORDS for word in words):
        return "greeting", 0.98

    # Explicit question punctuation is a strong signal.
    if "?" in text:
        return "question", 0.95

    # Question-style openings.
    if text.startswith(QUESTION_STARTERS):
        return "question", 0.88

    # Explicit command-style openings.
    if text.startswith(COMMAND_STARTERS):
        return "command", 0.90

    return "statement", 0.72


def _detect_emotion(message: str) -> tuple[str, float]:
    """Detect the dominant emotion using deterministic keyword rules."""
    text = _normalize(message)

    # More specific emotional states get priority.
    if _contains_any(text, FRUSTRATION_WORDS):
        return "frustrated", 0.92

    if _contains_any(text, HOSTILE_WORDS):
        return "negative", 0.90

    if _contains_any(text, CONFIDENT_WORDS):
        return "confident", 0.88

    if _contains_any(text, PLAYFUL_WORDS):
        return "playful", 0.86

    if _contains_any(text, POSITIVE_WORDS):
        return "positive", 0.85

    if _contains_any(text, NEGATIVE_WORDS):
        return "negative", 0.84

    # Questions containing uncertainty markers are treated as confused.
    confusion_markers = (
        "i don't understand",
        "i dont understand",
        "confused",
        "what do you mean",
        "how am i supposed",
    )

    if _contains_any(text, confusion_markers):
        return "confused", 0.84

    return "neutral", 0.65


def _detect_topic(message: str) -> str:
    """Detect the first recognizable topic."""
    text = _normalize(message)

    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return topic

    return "general"


def _calculate_hostility(message: str) -> float:
    """Calculate a deterministic hostility score from 0.0 to 1.0."""
    text = _normalize(message)

    matches = sum(1 for word in HOSTILE_WORDS if word in text)

    if matches == 0:
        return 0.0

    if matches == 1:
        return 0.55

    if matches == 2:
        return 0.75

    return 0.9


def _calculate_challenge(
    message: str,
    emotion: str,
    hostility_level: float,
) -> float:
    """Calculate how strongly the message invites competitive interaction."""
    text = _normalize(message)

    score = 0.15

    if "?" in text:
        score += 0.10

    if emotion == "confident":
        score += 0.30

    if emotion == "playful":
        score += 0.15

    if emotion == "frustrated":
        score += 0.20

    if hostility_level > 0:
        score += 0.35

    if _contains_any(text, CONFIDENT_WORDS):
        score += 0.10

    return min(round(score, 2), 1.0)


def analyze_message(message: str) -> dict:
    """
    Analyze a user message and return structured information.

    The function is deterministic and does not call any external service.
    """
    if not isinstance(message, str):
        raise TypeError("message must be a string")

    intent, intent_confidence = _detect_intent(message)
    emotion, emotion_confidence = _detect_emotion(message)
    topic = _detect_topic(message)
    hostility_level = _calculate_hostility(message)
    challenge_level = _calculate_challenge(
        message,
        emotion,
        hostility_level,
    )

    confidence = round(
        (intent_confidence + emotion_confidence) / 2,
        2,
    )

    return {
        "intent": intent,
        "emotion": emotion,
        "topic": topic,
        "challenge_level": challenge_level,
        "hostility_level": hostility_level,
        "confidence": confidence,
    }