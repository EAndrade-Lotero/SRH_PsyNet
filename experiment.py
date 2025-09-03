# pylint: disable=unused-import,abstract-method,unused-argument
##########################################################################################
# Imports
##########################################################################################
from markupsafe import Markup

import psynet.experiment
from psynet.modular_page import (
    ImagePrompt, ModularPage, 
    PushButtonControl, NumberControl,
    NullControl
)
from psynet.timeline import Timeline
from psynet.trial.create_and_rate import (
    CreateAndRateNode,
    CreateAndRateTrialMakerMixin,
    CreateTrialMixin,
    RateTrialMixin,
)
from psynet.trial.imitation_chain import ImitationChainTrial, ImitationChainTrialMaker
from psynet.utils import get_logger

logger = get_logger()


##########################################################################################
NUM_FORAGERS = 2
##########################################################################################


def positioning_prompt(text, img_url):
    return ImagePrompt(
        url=img_url,
        text=Markup(text),
        width="475px",
        height="300px",
    )


class CoordinatorTrial(CreateTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant):
        forager_id = (participant.id - 1) % NUM_FORAGERS
        # return PageMaker(
        #         lambda: InfoPage(f"Where do you want to locate forager {forager_id}?"),
        #         time_estimate=5,
        #     )
        return ModularPage(
                "create_trial",
                positioning_prompt(
                    text=f"Where do you want to locate forager {forager_id}?", 
                    img_url=self.context["img_url"]
                ),
                NumberControl(),
                time_estimate=self.time_estimate,
            ),


class ForagerTrial(RateTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant):
        assert self.trial_maker.target_selection_method == "one"

        assert len(self.targets) == 1
        target = self.targets[0]
        creation = self.get_target_answer(target)
        return ModularPage(
            "rate_trial",
            positioning_prompt(
                text=f"You have been located here:<br><strong>{target}</strong><br><strong>{creation}</strong>",
                img_url=self.context["img_url"],
            ),
            PushButtonControl(
                choices=[1],
                labels=["Continue"],
                arrange_vertically=False,
            ),
        )


class CreateAndRateTrialMaker(CreateAndRateTrialMakerMixin, ImitationChainTrialMaker):
    pass


##########################################################################################
# Experiment
##########################################################################################


def get_trial_maker():
    rater_class = ForagerTrial
    n_creators = 1
    n_raters = 2
    rate_mode = "rate"
    include_previous_iteration = True
    target_selection_method = "one"

    start_nodes = [
        CreateAndRateNode(context={"img_url": "static/positioning.png"}, seed="initial creation")
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


###########################
# Questions

# 1. I updated something in the code, saved and when I run the experiment,
#    I get an ERROR:root:EXPERIMENT ERROR. Neither refreshing nor restarting
#    the experiment seem to help. I'm sure the error doesn't come from my code,
#    it comes from psynet. What is happening?
#
# 2. The trials seem to be running only with ModularPage, but not with 
#    Module or PageMaker. I need to use PageMaker or Module to be able to
#    include more functionalities for the participants. Why is this happening?
#
# 3. Suppose I make the coordinator position two foragers. How do I have access
#    to the positions of both foragers in the forager trial?
###########################
