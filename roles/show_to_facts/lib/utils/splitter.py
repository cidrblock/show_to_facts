import re

def section_split(regex, lines):
    sections = []
    section = ()
    capturing = False
    for line in lines:
        if re.match(regex, line):
            if not capturing:
                capturing = True
            else:
                if section:
                    sections.append(section)
            section = (line,[])
        elif capturing:
            section[1].append(line)
    sections.append(section)
    return sections