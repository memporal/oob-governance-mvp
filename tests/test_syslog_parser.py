import pytest

from app.ingestion.syslog import parse_syslog_line


@pytest.mark.parametrize(
    "line,site,link,asn",
    [
        ("<134>1 ts host app - - - site=site-a link=wan1 asn=64512", "site-a", "wan1", 64512),
        ("site=site-b link=wan2 asn=64513", "site-b", "wan2", 64513),
        ("foo bar site=nyc-1 link=primary asn=65000 baz", "nyc-1", "primary", 65000),
        ("site=lab_01 link=lte_backup asn=65123", "lab_01", "lte_backup", 65123),
        ("prefix site=s1 link=l1 asn=1 suffix", "s1", "l1", 1),
    ],
)
def test_parse_syslog_line(line, site, link, asn):
    parsed = parse_syslog_line(line)
    assert parsed["site"] == site
    assert parsed["link"] == link
    assert parsed["asn"] == asn


def test_parse_syslog_line_invalid():
    with pytest.raises(ValueError):
        parse_syslog_line("no fields here")
