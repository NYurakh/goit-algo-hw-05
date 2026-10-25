import timeit
from pathlib import Path

# region Algorithms


# * Боєр-Мур 
def boyer_moore(text, pattern):
    if not pattern:
        return 0

    last = {ch: i for i, ch in enumerate(pattern)}
    m = len(pattern)
    i = 0

    while i <= len(text) - m:
        j = m - 1

        while j >= 0 and pattern[j] == text[i + j]:
            j -= 1

        if j < 0:
            return i

        i += max(1, j - last.get(text[i + j], -1))

    return -1


# * Кнут-Морріс-Пратт
def kmp(text, pattern):
    if not pattern:
        return 0

    m = len(pattern)
    lps = [0] * m
    j = 0

    # Побудова таблиці префіксів
    for i in range(1, m):
        while j > 0 and pattern[i] != pattern[j]:
            j = lps[j - 1]

        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j

    # Пошук підрядка
    j = 0
    for i in range(len(text)):
        while j > 0 and text[i] != pattern[j]:
            j = lps[j - 1]

        if text[i] == pattern[j]:
            j += 1

        if j == m:
            return i - m + 1

    return -1


# * Рабін-Карп 
def rabin_karp(text, pattern):
    if not pattern:
        return 0

    n, m = len(text), len(pattern)
    if m > n:
        return -1

    base = 256
    mod = 101
    pattern_hash = 0
    window_hash = 0
    power = pow(base, m - 1, mod)

    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % mod
        window_hash = (window_hash * base + ord(text[i])) % mod

    for i in range(n - m + 1):
        # ! Збіг хешів не гарантує збігу рядків - перевіряємо підрядок
        if pattern_hash == window_hash and text[i : i + m] == pattern:
            return i

        if i < n - m:
            window_hash = (
                (window_hash - ord(text[i]) * power) * base + ord(text[i + m])
            ) % mod

    return -1


# endregion

# region Settings

algorithms = {
    "Boyer-Moore": boyer_moore,
    "KMP": kmp,
    "Rabin-Karp": rabin_karp,
}

PATTERNS = {
    "article1.txt": (
        ("Існує", "Інтерполяційний пошук"),
        ("Не існує", "qwertyuiopxyz"),
    ),
    "article2.txt": (
        ("Існує", "орієнтованого ациклічного графу"),
        ("Не існує", "qwertyuiopxyz"),
    ),
}

REPEAT = 5  # + кількість серій вимірювань (беремо найкращу)
NUMBER = 5  # + кількість викликів у серії

# endregion

# region Helpers


def fix_mojibake(text):
    # ! Були помилки з файлами, які не були в кодуванні UTF-8, а в Windows-1251 (CP1251). Тому для перестраховки додав цю функцію.
    try:
        fixed = text.encode("cp1252").decode("cp1251")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

    def cyrillic(s):
        return sum("Ѐ" <= ch <= "ӿ" for ch in s)

    return fixed if cyrillic(fixed) > cyrillic(text) else text


def read_text(filename):
    try:
        text = Path(filename).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = Path(filename).read_text(encoding="cp1251")
    return fix_mojibake(text)


# endregion

# region Benchmark


def main():
    total_times = {name: 0 for name in algorithms}

    for filename, patterns in PATTERNS.items():
        text = read_text(filename)

        print(f"\n--- {filename} ({len(text)} символів) ---")
        file_times = {name: 0 for name in algorithms}

        for kind, pattern in patterns:
            assert (pattern in text) == (kind == "Існує")

            print(f"\n{kind}: {pattern!r}")

            for name, func in algorithms.items():
                assert func(text, pattern) == text.find(pattern)

                runs = timeit.repeat(
                    lambda: func(text, pattern),
                    repeat=REPEAT,
                    number=NUMBER,
                )
                elapsed = min(runs) / NUMBER

                file_times[name] += elapsed
                print(f"{name}: {elapsed * 1000:.4f} мс")

        winner = min(file_times, key=file_times.get)
        print(f"\nНайшвидший для {filename}: {winner}")

        for name in algorithms:
            total_times[name] += file_times[name]

    print("\n--- Загальний результат ---")
    for name, t in total_times.items():
        print(f"{name}: {t * 1000:.4f} мс")
    print(f"Найшвидший: {min(total_times, key=total_times.get)}")


# endregion

if __name__ == "__main__":
    main()
