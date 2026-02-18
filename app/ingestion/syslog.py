import re

SYSLOG_PATTERN = re.compile(
    r"site=(?P<site>[a-zA-Z0-9_-]+)\s+link=(?P<link>[a-zA-Z0-9_-]+)\s+asn=(?P<asn>\d+)"
)


def parse_syslog_line(line: str) -> dict[str, str | int]:
    match = SYSLOG_PATTERN.search(line)
    if not match:
        raise ValueError(f"Unable to parse syslog line: {line}")
    data = match.groupdict()
    return {"site": data["site"], "link": data["link"], "asn": int(data["asn"]), "raw": line}
