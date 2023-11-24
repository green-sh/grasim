
def test_parse():
    from grasim import savefile

    savefile.parse_text("""
A -0- B
START A
END B
                        """.splitlines())

test_parse()