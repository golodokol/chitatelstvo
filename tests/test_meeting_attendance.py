from catalog.loader import get_module
from services.meeting_attendance import list_tales_for_enrollment


class _Enrollment:
    def __init__(self, *, chosen_stage: str, chosen_tale_number: int | None = None, chosen_tale_title: str | None = None):
        self.chosen_stage = chosen_stage
        self.chosen_tale_number = chosen_tale_number
        self.chosen_tale_title = chosen_tale_title


def test_list_tales_for_single_enrollment():
    module = get_module(1)
    enrollment = _Enrollment(chosen_stage="1", chosen_tale_number=1)
    titles = list_tales_for_enrollment(module, enrollment)
    assert titles == ["Царевна лягушка"]


def test_list_tales_for_block_enrollment():
    module = get_module(3)
    enrollment = _Enrollment(chosen_stage="1")
    titles = list_tales_for_enrollment(module, enrollment)
    assert len(titles) == 4
    assert titles[0] == "Царевна лягушка"
