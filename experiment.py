# pylint: disable=unused-import,abstract-method,unused-argument
##########################################################################################
# Imports
##########################################################################################
import re

from typing import (
    List, Tuple, Union, Any
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

from .helper_functions import (
    get_list_participants_ids,
)
from .custom_front_end import (
    HelloPrompt,
    positioning_prompt,
    ColorText,
)

logger = get_logger()

NUM_FORAGERS = 3


###########################################
# Coordinator classes
###########################################

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
            AssignForagersPage(
                context=self.context,
                num_foragers=NUM_FORAGERS,
                time_estimate=self.time_estimate,
                bot_response="23, 42" 
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
        ]
        return list_of_pages
    
###########################################


###########################################
# Forager classes
###########################################

class ForagerTrial(SelectTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant) -> List[Any]:
        
        assert self.trial_maker.target_selection_method == "all"

        # There should be only one target
        targets = [target for target in self.targets if isinstance(target, CoordinatorTrial)]
        assert(len(targets) == 1), f"Error: Num. targets should be 1 but got {len(targets)}!"

        # Get target from coordinator
        target = targets[0]
        if isinstance(target, CreateAndRateNode):
            target = self.get_target_answer(target)
        assert isinstance(target, CoordinatorTrial)            

        # Get list of positions from target
        positions = self.get_target_answer(target)
        logger.info(f"positions: {positions}")

        # Get participant info
        logger.info(f"My id is: {participant.id}")

        # Get list of previous participants
        participants_id = get_list_participants_ids(experiment, participant)
        # Calculate id based on number of previous non failed participants
        forager_id = (len(participants_id) % (NUM_FORAGERS + 1)) - 1

        logger.info(f"forager id: {forager_id}")

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
                    choices=[f"{target}" for target in targets],
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
    label = "Social roles and hierarchies skeleton experiment"
    initial_recruitment_size = 1

    timeline = Timeline(
        get_trial_maker(),
    )

    # test_n_bots = 6

###########################################