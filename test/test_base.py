from scribdl.content.base import ScribdBase

import pytest


def test_abstract_class():
    with pytest.raises(TypeError):
        x = ScribdBase()
