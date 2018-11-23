from scribdl.base import ScribdBase

import pytest


class TestOverrideScribdBase(ScribdBase):
    def get_content(self):
        pass

def test_abstract_class():
    with pytest.raises(TypeError):
        x = ScribdBase()
