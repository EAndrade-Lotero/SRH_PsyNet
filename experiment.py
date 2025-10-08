# pylint: disable=unused-import,abstract-method,unused-argument
##########################################################################################
# Imports
##########################################################################################
import re

from typing import (
    List, Union, Any
)
from markupsafe import Markup

import psynet.experiment
from psynet.page import  InfoPage
from psynet.utils import get_logger
from psynet.timeline import (
    Timeline,
    FailedValidation,
)
from psynet.modular_page import (
    ModularPage, 
    Prompt, 
    ImagePrompt,
    Control, 
    PushButtonControl,
    TextControl,
)
from psynet.trial.create_and_rate import (
    CreateAndRateNode,
    CreateAndRateTrialMakerMixin,
    CreateTrialMixin,
    RateTrialMixin,
    SelectTrialMixin,
)
from psynet.trial.imitation_chain import (
    ImitationChainTrial, 
    ImitationChainTrialMaker
)

# from .coordinator import CoordinatorTrial
# from .helper_functions import positioning_prompt

logger = get_logger()

NUM_FORAGERS = 3

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
    ) -> None:
        super().__init__(text=text, text_align=text_align)
        self.username = username

class ColorText(Control):
    macro = "color_text_area"
    external_template = "custom-controls.html"

    def __init__(self, color) -> None:
        super().__init__()
        self.color = color

    @property
    def metadata(self):
        return {"color": self.color}

class AssignForagersPage(ModularPage):
    def __init__(
        self, 
        context: Any,
        num_foragers: int,
        time_estimate: float, 
        bot_response: Any
    ) -> None:

        super().__init__(
            "create_trial",
            positioning_prompt(
                text=f"Write the coordinates of the foragers, separated by colons", 
                img_url=context["img_url"]
            ),
            TextControl(
                block_copy_paste=True,
                bot_response=bot_response,
            ),
            time_estimate=time_estimate,
        )
        self.num_foragers = num_foragers

    def format_answer(self, raw_answer, **kwargs) -> Union[List[int], str]:
        try:
            numbers = re.findall(r"-?\d+", raw_answer)
            assert len(numbers) == self.num_foragers
            numbers = [int(n) for n in numbers]
            logger.info(f"------> numbers input: {numbers}")
            return numbers
        except (ValueError, AssertionError):
            return f"INVALID_RESPONSE"

    def validate(self, response, **kwargs) -> Union[bool, None]:
        logger.info(f"Validating...")
        if response.answer == "INVALID_RESPONSE":
            logger.info(f"Invalid response!")
            return FailedValidation(f"Please enter {self.num_foragers} numbers separated by colons")
        logger.info(f"Validated!")
        return None

###########################################


###########################################
# Coordinator classes
###########################################

class CoordinatorTrial(CreateTrialMixin, ImitationChainTrial):
    time_estimate = 5
    num_foragers = NUM_FORAGERS

    def show_trial(self, experiment, participant) -> List[Any]:
        logger.info("Entering the coordinator trial...")
        experiment.var.set("forager_counter", 0)
        list_of_pages = [
            InfoPage(
                "This is going to be the Instructions page for the COORDINATOR",
                time_estimate=5
            ),
            # ModularPage(
            #     "test_custom_front_end",
            #     HelloPrompt(
            #         username=f"{participant.id}",
            #         text="Please position the foragers on the map below."
            #     ),
            #     ColorText(
            #         color='#FFD580;'
            #     ),
            #     time_estimate=self.time_estimate
            # ),
            AssignForagersPage(
                context=self.context,
                num_foragers=NUM_FORAGERS,
                time_estimate=self.time_estimate,
                bot_response="23, 42" 
            )
        ]
        return list_of_pages
    
###########################################


###########################################
# Forager classes
###########################################

class ForagerTrial(SelectTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant):
        # Get targets from coordinator. There should be only one target
        assert self.trial_maker.target_selection_method == "all"
        targets = [target for target in self.targets if isinstance(target, CoordinatorTrial)]
        logger.info(f"{len(targets)=}")
        assert(len(targets) == 1), f"Error: Num. targets should be 1 but got {len(targets)}!"
        choices = [f"{target}" for target in targets]
        target = targets[0]

        # Get list of positions from target
        if isinstance(target, CreateAndRateNode):
            target = self.get_target_answer(target)
        assert isinstance(target, CoordinatorTrial)            
        positions = self.get_target_answer(target)
        logger.info(f"positions: {positions}")

        # Get forager id
        forager_counter = experiment.var.forager_counter
        logger.info(f"Forager counter: {forager_counter}")
        forager_id = forager_counter % NUM_FORAGERS
        assert(forager_id in list(range(NUM_FORAGERS))), f"Error: Forager id should be one of {list(range(NUM_FORAGERS))} but got {forager_id}!"
        logger.info(f"forager id: {forager_id}")
        forager_counter += 1
        experiment.var.set("forager_counter", forager_counter)

        # Extract forager position
        location = positions[forager_id]
        
        list_of_pages = [
            # InfoPage(
            #     "This is going to be the Instructions page for a FORAGER",
            #     time_estimate=5
            # ),
            ModularPage(
                "forager_turn",
                positioning_prompt(
                    text=f"You have been located here:<br><strong>{location}</strong>",
                    img_url=self.context["img_url"],
                ),
                PushButtonControl(
                    choices=choices,
                    labels=["Continue"],
                    arrange_vertically=False,
                ),
                time_estimate=self.time_estimate
            ),
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
    # rate_mode = "rate"
    rate_mode = "select"
    include_previous_iteration = True
    target_selection_method = "all"

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
        max_nodes_per_chain=NUM_FORAGERS,
    )

class Exp(psynet.experiment.Experiment):
    label = "Basic Create and Rate Experiment"
    initial_recruitment_size = 1
    variables = {
            "forager_counter": 0,
    }

    timeline = Timeline(
        get_trial_maker(),
    )

    # test_n_bots = 6

###########################################