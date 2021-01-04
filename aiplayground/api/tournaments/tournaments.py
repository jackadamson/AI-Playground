from typing import Dict, List

from aiplayground.api.bots import Bot
from aiplayground.api.tournaments.models import Participant, Tournament, Match, PlayerQueueEntry, MatchState
from collections import defaultdict

import operator

from aiplayground.exceptions import AlreadyInTournament
from aiplayground.logging import logger
from aiplayground.types import PlayerSID


def add_player(bot: Bot, tournament: Tournament) -> Participant:
    logger.debug("Getting tournament lock: %s", tournament.id)
    with tournament.lock():
        logger.debug("Got lock for tournament: %s", tournament.id)
        participants = tournament.participants
        participant_ids = {participant.bot.id for participant in participants}
        if bot.id in participant_ids:
            raise AlreadyInTournament
        index = max(x.index for x in participants) + 1 if participants else 1
        participant = Participant.create(index=index, bot=bot, tournament=tournament)
        for opponent in participants:
            if opponent.disqualified:
                continue
            Match.create(
                index=100000 * index + opponent.index,
                tournament=tournament,
                players=[participant, opponent],
                state=MatchState.pending,
            )
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
