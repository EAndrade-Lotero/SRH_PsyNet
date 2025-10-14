# Module with custom prompts and controls

##########################################################################################
# Imports
##########################################################################################

from typing import Union
from markupsafe import Markup

from psynet.modular_page import (
    Prompt, 
    ImagePrompt,
    Control,
)


###########################################
# Custom prompts
###########################################

def positioning_prompt(text, img_url) -> Prompt:
    return ImagePrompt(
        url=img_url,
        text=Markup(text),
        width="475px",
        height="300px",
    )

class HelloPrompt(Prompt):
    macro = "with_hello"
    external_template = "custom-prompts.html"

    def __init__(
            self,
            username: str,
            text: Union[None, str, Markup] = None,
            text_align: str = "left",
    ) -> None:
        super().__init__(text=text, text_align=text_align)
        self.username = username


###########################################
# Custom controls
###########################################

class ColorText(Control):
    macro = "color_text_area"
    external_template = "custom-controls.html"

    def __init__(self, color) -> None:
        super().__init__()
        self.color = color

    @property
    def metadata(self):
        return {"color": self.color}

###########################################
