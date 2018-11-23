import sys


def fix_encoding(query):
    """
    Encoding fixes for Python 2 and Python 3 cross-compatibilty.
    """
    if sys.version_info > (3, 0):
        return query
    else:
        return query.encode('utf-8')


def sanitize_title(title):
    """
    Remove forbidden characters from title that will prevent Windows
    from creating directory.

    Also change ' ' to '_' to preserve previous behavior.
    """
    forbidden_chars = " *\"/\<>:|(),"
    replace_char = "_"

    for ch in forbidden_chars:
        title = title.replace(ch, replace_char)

    return title


