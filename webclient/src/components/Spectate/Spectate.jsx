import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Typography } from '@material-ui/core';
import axios from 'axios';
import Chip from '@material-ui/core/Chip';
import Container from '@material-ui/core/Container';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import socketio from '../../socketio';
import Games from '../Games';
import { successColor, primaryColor, infoColor } from '../../assets/styles/commonStyles';
import useStyles from './styles';

const capitalize = (lower) => (lower ? lower.charAt(0).toUpperCase() + lower.substring(1) : '');
const statusColors = { finished: successColor[1], playing: primaryColor[1], lobby: infoColor[3] };
const getColor = (status) => (status === undefined ? '' : statusColors[status]);

const Spectate = ({ match: { params: { roomId } } }) => {
  const classes = useStyles();
  const [room, setRoom] = useState({});
  const [board, setBoard] = useState(null);
  useEffect(() => {
    axios.get(`/rooms/${roomId}`).then((resp) => {
      setRoom(resp.data);
    });
  }, [roomId]);
  useEffect(() => {
    if (room.game) {
      return;
    }
    const update = (data) => {
      console.log(data);
      console.log(room);
      console.log({ ...room, turn: data.turn, board: data.board });
      setBoard(data.board);
    };
    const s = socketio.on('gamestate', update);
    socketio.emit('spectate', { roomid: roomId }, (_, data) => {
      setBoard(data.board);
    });
  }, [room]);

  const Game = Games[room.game];
  return (
    <>
      <div className={classes.mainArea}>
        <Typography component="h5" variant="h5">
          Asimov's Playground
        </Typography>
        <Typography variant="h6">
          {`Spectating ${room.name}`}
        </Typography>
        <span>
State:
          <Chip label={capitalize(room.status)} style={{ backgroundColor: getColor(room.status) }} />
        </span>
        <Container className={classes.mainArea}>
          {board && Game ? <Game board={board} /> : (<Typography variant="body2">Game not started</Typography>)}
        </Container>
      </div>
      <Drawer variant="permanent" anchor="right" className={classes.playerDrawer}>
        <Container className={classes.playerDrawerInner}>
          <Typography variant="subtitle2">Players</Typography>
          {room.players ? (
            <List>
              {room.players.map((player) => (
                <ListItem key={player.id}>
                  <ListItemText primary={player.name} />
                </ListItem>
              ))}
            </List>
          ) : null}
        </Container>
      </Drawer>
    </>
  );
};
Spectate.propTypes = {
  match: PropTypes.shape({ params: PropTypes.shape({ roomId: PropTypes.string.isRequired }) }).isRequired,
};
export default Spectate;
