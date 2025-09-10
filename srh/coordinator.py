# # Classes for the coordinator POV

# from psynet.page import  InfoPage
# from psynet.trial.create_and_rate import (
#     CreateTrialMixin,
# )
# from psynet.modular_page import (
#     ModularPage, TextControl
# )
# from psynet.trial.imitation_chain import ImitationChainTrial
# from psynet.utils import get_logger

# logger = get_logger()


# def positioning_prompt(text, img_url):
#     return ImagePrompt(
#         url=img_url,
#         text=Markup(text),
#         width="475px",
#         height="300px",
#     )


class CoordinatorTrial(CreateTrialMixin, ImitationChainTrial):
    time_estimate = 5

    def show_trial(self, experiment, participant):
        list_of_pages = [
            InfoPage(
                "Ok",
                time_estimate=5
            ),
            # ModularPage(
            #     "create_trial",
            #     positioning_prompt(
            #         text=f"Write the coordinates of the foragers, separated by colons", 
            #         img_url=self.context["img_url"]
            #     ),
            #     TextControl(),
            #     time_estimate=self.time_estimate,
            #     bot_response="23, 42" 
            # )
        ]
        return list_of_pages


# class CustomTrial(ImitationChainTrial):
#     accumulate_answers = True
#     time_estimate = 5 + 3 + 3

#     def show_trial(self, experiment, participant):
#         page_1 = InfoPage(
#             f"Try to remember this 7-digit number: {self.definition:07d}",
#             time_estimate=5,
#         )
#         page_2 = FixedDigitInputPage(
#             "number_1",
#             "What was the number?",
#             time_estimate=3,
#             bot_response=lambda: self.definition,
#         )
#         page_3 = FixedDigitInputPage(
#             "number_2",
#             "Type the number one more time.",
#             time_estimate=3,
#             bot_response=lambda: self.definition,
#         )
#         return [page_1, page_2, page_3]