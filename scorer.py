def judge(question, expects, answer, results) -> bool:
    """Return True if the answer is correct, False if not.

    This is a simple example of a judge function. You can write your own
    more sophisticated one, but it must have the same signature and return
    type.

    `question` is the question string.
    `expects` is the string you expect to see in a correct answer.
    `answer` is the string returned by your system.
    `results` is a list of dicts with the retrieval results, which you can
        use to make your decision if you want.

    """

    if not expects:
        return False
    return expects.strip().lower() in (answer or "".lower)

