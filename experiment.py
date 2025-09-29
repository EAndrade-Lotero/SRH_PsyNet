# pylint: disable=unused-import,abstract-method,unused-argument
##########################################################################################
# Imports
##########################################################################################
import re

from typing import Union
from markupsafe import Markup

import psynet.experiment
from psynet.page import  InfoPage
from psynet.modular_page import (
    ModularPage, 
    Prompt, ImagePrompt,
    Control, PushButtonControl,
    TextControl, NullControl
)
from psynet.timeline import Timeline
from psynet.trial.create_and_rate import (
    CreateAndRateNode,
    CreateAndRateTrialMakerMixin,
    CreateTrialMixin,
    RateTrialMixin,
    SelectTrialMixin,
)
from psynet.trial.imitation_chain import ImitationChainTrial, ImitationChainTrialMaker
from psynet.utils import get_logger

# from .coordinator import CoordinatorTrial
# from .helper_functions import positioning_prompt

logger = get_logger()

NUM_FORAGERS = 2

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
# Helper functions
###########################################

def positioning_prompt(text, img_url):
    return ImagePrompt(
        url=img_url,
        text=Markup(text),
        width="475px",
        height="300px",
    )
###########################################


###########################################
# Coordinator classes
###########################################

class CoordinatorTrial(CreateTrialMixin, ImitationChainTrial):
    time_estimate = 5
    num_foragers = NUM_FORAGERS

    def show_trial(self, experiment, participant):
        list_of_pages = [
            InfoPage(
                "This is going to be the Instructions page for the COORDINATOR",
                time_estimate=5
            ),
            ModularPage(
                "test_custom_front_end",
                HelloPrompt(
                    username=f"{participant.id}",
                    text="Please position the foragers on the map below."
                ),
                ColorText(
                    color='#FFD580;'
                ),
                time_estimate=self.time_estimate
            ),
            ModularPage(
                "create_trial",
                positioning_prompt(
                    text=f"Write the coordinates of the foragers, separated by colons", 
                    img_url=self.context["img_url"]
                ),
                TextControl(),
                time_estimate=self.time_estimate,
                # bot_response="23, 42" 
            )
        ]
        return list_of_pages
    
    def format_answer(self, raw_answer, **kwargs):
        try:
            numbers = re.findall(r"-?\d+", raw_answer)
            numbers = [int(n) for n in numbers]
            return numbers
        except (ValueError, AssertionError):
            return "INVALID_RESPONSE"

    def validate(self, response, **kwargs):
        if response.answer == "INVALID_RESPONSE":
            return FailedValidation(f"Please enter {self.num_foragers} numbers separated by colons")
        return None

###########################################


###########################################
# Forager classes
###########################################

class ForagerTrial(RateTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant):
        assert self.trial_maker.target_selection_method == "one"
        assert len(self.targets) == 1
        target = self.targets[0]
        positions = self.get_target_answer(target)
        forager_id = (participant.id - 1) % NUM_FORAGERS
        try:
            location = positions[forager_id]
        except:
            location = positions
        
        list_of_pages = [
            InfoPage(
                "This is going to be the Instructions page for a FORAGER",
                time_estimate=5
            ),
            ModularPage(
                "rate_trial",
                positioning_prompt(
                    text=f"You have been located here:<br><strong>{location}</strong>",
                    img_url=self.context["img_url"],
                ),
                PushButtonControl(
                    choices=[1],
                    labels=["Continue"],
                    arrange_vertically=False,
                ),
                time_estimate=self.time_estimate
            )
        ]
        return list_of_pages
###########################################

###########################################
###########################################
# Experiment
###########################################

class CreateAndRateTrialMaker(CreateAndRateTrialMakerMixin, ImitationChainTrialMaker):
    pass

def get_trial_maker():
    rater_class = ForagerTrial
    n_creators = 1
    n_raters = NUM_FORAGERS
    rate_mode = "rate"
    include_previous_iteration = True
    target_selection_method = "one"

    start_nodes = [
        CreateAndRateNode(
            context={"img_url": "static/positioning.png"}, 
            seed="initial creation"
        )
    ]

    return CreateAndRateTrialMaker(
        n_creators=n_creators,
        n_raters=n_raters,
        node_class=CreateAndRateNode,
        creator_class=CoordinatorTrial,
        rater_class=rater_class,
        # mixin params
        include_previous_iteration=include_previous_iteration,
        rate_mode=rate_mode,
        target_selection_method=target_selection_method,
        verbose=True,  # for the demo
        # trial_maker params
        id_="create_and_rate_basic",
        chain_type="across",
        expected_trials_per_participant=len(start_nodes),
        max_trials_per_participant=len(start_nodes),
        start_nodes=start_nodes,
        chains_per_experiment=len(start_nodes),
        balance_across_chains=False,
        check_performance_at_end=True,
        check_performance_every_trial=False,
        propagate_failure=False,
        recruit_mode="n_trials",
        target_n_participants=None,
        wait_for_networks=False,
        max_nodes_per_chain=10,
    )

class Exp(psynet.experiment.Experiment):
    label = "Basic Create and Rate Experiment"
    initial_recruitment_size = 1

    timeline = Timeline(
        get_trial_maker(),
    )

    # test_n_bots = 6

###########################################