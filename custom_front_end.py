##########################################################################################
# Imports
##########################################################################################

from typing import Union
from markupsafe import Markup

from psynet.modular_page import Prompt, Control


###########################################
# Custom front ends
###########################################
class HelloPrompt(Prompt):
    macro = "with_hello"
    external_template = "custom-prompts.html"

    def __init__(
            self,
            username: str,
            text: Union[None, str, Markup] = None,
            text_align: str = "left",
    ):
        super().__init__(text=text, text_align=text_align)
        self.username = username

class ColorText(Control):
    macro = "color_text_area"
    external_template = "custom-controls.html"

    def __init__(self, color):
        super().__init__()
        self.color = color

    @property
    def metadata(self):
        return {"color": self.color}

###########################################
