# every model has to be imported here so that Base.metadata knows about
# it before main.py calls Base.metadata.create_all(). if a model is left
# out of this file, its table simply never gets created.
from .teams import Team
from .player import Player
from .fixture import Fixture
from .match_event import MatchEvent
from .venue import Venue
from .competition import Competition
from .season import Season
from .standings import Standing
from .playerstatistic import PlayerStatistic
from .matchstatistic import MatchStatistic
from .teamstatistic import TeamStatistic
from .announcement import Announcement, AnnouncementStatus, AnnouncementType
from .user import User