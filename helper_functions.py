# Module with the helper functions

##########################################################################################
# Imports
##########################################################################################

from markupsafe import Markup

import psynet
from psynet.utils import get_logger

logger = get_logger()

###########################################
# Helper functions
###########################################

def get_list_participants_ids(
        experiment: psynet.experiment.Experiment, 
        participant: psynet.participant.Participant
    ) -> int:
    
    # Get previous participant's ids
    participants_id = []
    for id in range(1, participant.id):
        try:
            p = experiment.get_participant_from_participant_id(id)
            if not p.failed:
                participants_id.append(id)
        except:
            pass
            logger.info(f"Id {id} is not valid!")

    logger.info(f"Participants: {participants_id}")

    return participants_id

