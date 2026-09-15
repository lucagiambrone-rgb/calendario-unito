import os
import urllib.request
from pathlib import Path

SOURCE_URL = os.environ["UNTO_ICAL_URL"]

KEEP_PREFIXES = (
    "Sist Inf - SISTEMI INFORMATIVI",
    "Reti & Sic A - RETI E SICUREZZA DELLE RETI",
    "TWeb - TECNOLOGIE WEB",
)


def unfold_ical(text):
    raw = text.splitlines(keepends=True)
    result = []

    for line in raw:
        if line.startswith((" ", "\t")) and result:
            result[-1] = result[-1].rstrip("\r\n") + line[1:]
        else:
            result.append(line)

    return result


def filter_calendar(text):
    lines = unfold_ical(text)

    result = []
    event = None
    keep = False

    for line in lines:

        if line.startswith("BEGIN:VEVENT"):
            event = [line]
            keep = False

        elif event is not None:
            event.append(line)

            if line.startswith("SUMMARY:"):
                summary = line[len("SUMMARY:"):].rstrip("\r\n")
                keep = any(
                    summary.startswith(prefix)
                    for prefix in KEEP_PREFIXES
                )

            if line.startswith("END:VEVENT"):
                if keep:
                    result.extend(event)

                event = None
                keep = False

        else:
            result.append(line)

    return "".join(result)


def main():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "calendario-unito/1.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        original = response.read().decode("utf-8")

    filtered = filter_calendar(original)

    output = Path("docs/calendario.ics")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(filtered, encoding="utf-8")

    print(
        "Calendario aggiornato:",
        filtered.count("BEGIN:VEVENT"),
        "eventi"
    )


if __name__ == "__main__":
    main()
