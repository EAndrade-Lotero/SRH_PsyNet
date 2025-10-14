# Module with the helper functions

from psynet.modular_page import (
    ImagePrompt, ModularPage, 
    PushButtonControl, NumberControl,
    TextControl
)


def positioning_prompt(text, img_url):
    return ImagePrompt(
        url=img_url,
        text=Markup(text),
        width="475px",
        height="300px",
    )


# def test_check_bots(self, bots: List[Bot]):
#     time.sleep(2.0)

#     assert len([b for b in bots if b.var.participant_group == "A"]) == 3
#     assert len([b for b in bots if b.var.participant_group == "B"]) == 3

#     for b in bots:
#         assert len(b.alive_trials) == 7  # 4 normal trials + 3 repeat trials
#         assert all([t.finalized for t in b.alive_trials])

#     processes = AsyncProcess.query.all()
#     assert all([not p.failed for p in processes])

#     super().test_check_bots(bots)


# def format_answer(self, raw_answer, **kwargs):
#     try:
#         pattern = re.compile("^[0-9]*$")
#         assert len(raw_answer) == self.n_digits
#         assert pattern.match(raw_answer)
#         return int(raw_answer)
#     except (ValueError, AssertionError):
#         return "INVALID_RESPONSE"

# def validate(self, response, **kwargs):
#     if response.answer == "INVALID_RESPONSE":
#         return FailedValidation("Please enter a 7-digit number.")
#     return None
