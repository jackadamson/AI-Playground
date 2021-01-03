from typing import Dict, List

from aiplayground.api.bots import Bot
from aiplayground.api.tournaments.models import Participant, Tournament, Match, PlayerQueueEntry, MatchState
from collections import defaultdict

import operator
from aiplayground.types import PlayerSID


def add_player(bot: Bot, tournament: Tournament) -> Participant:
    with tournament.lock():
        participants = tournament.participants
        index = max(x.index for x in participants) + 1
        participant = Participant.create(index=index, bot=bot, tournament=tournament)
        for opponent in participants:
            if opponent.disqualified:
                continue
            Match.create(index=100000 * index + opponent.index, tournament=tournament, players=[participant, opponent])
        return participant


def pick_match(tournament: Tournament) -> Match:
    with tournament.lock():
        queued_players = PlayerQueueEntry.list(tournament_id=tournament.id)
        participants_by_id = {participant.id: participant for participant in tournament.participants}
        participant_sids: Dict[Participant, List[PlayerSID]] = defaultdict(default_factory=list)
        for player in queued_players:
            participant = participants_by_id[player.participant_id]
            participant_sids[participant].append(player.sid)
        online_participants = set(participant_sids)
        matches = [
            match
            for match in tournament.matches
            if match.state == MatchState.pending and not set(match.players) - online_participants
        ]
        sorted_matches = sorted(matches, key=operator.attrgetter("index"))
        match = sorted_matches[0]
        match.state = MatchState.running
        match.save()
        return match
