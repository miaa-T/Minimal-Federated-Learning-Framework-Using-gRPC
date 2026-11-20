from dataclasses import dataclass
from enum import Enum


class ParticipantStatus(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"


@dataclass
class ParticipantInfo:
    participant_id: str
    status: ParticipantStatus = ParticipantStatus.IDLE
