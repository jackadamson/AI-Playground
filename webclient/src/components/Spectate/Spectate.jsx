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
import MobileStepper from '@material-ui/core/MobileStepper';
import Button from '@material-ui/core/Button';
import { KeyboardArrowLeft, KeyboardArrowRight, FirstPage, LastPage } from '@material-ui/icons';
import history from '../../history';
import socketio from '../../socketio';
import Games from '../games';
import { infoColor, primaryColor, successColor } from '../../assets/styles/commonStyles';
import useStyles from './styles';

const capitalize = (lower) => (lower ? lower.charAt(0).toUpperCase() + lower.substring(1) : '');
const statusColors = { finished: successColor[1], playing: primaryColor[1], lobby: infoColor[3] };
const getColor = (status) => (status === undefined ? '' : statusColors[status]);

const Spectate = ({ match: { params: { roomId } } }) => {
  const sortByEpoch = (s) => ([...s].sort((a, b) => (a.epoch - b.epoch)));
  const classes = useStyles();
  const [epoch, setEpoch] = useState(null);
  const [states, setStates] = useState([]);
  const [room, setRoom] = useState({
    players: [],
  });
  useEffect(() => {
    axios.get(`/rooms/${roomId}`).then((resp) => {
      setStates(resp.data.states);
      setRoom(resp.data);
    }).catch((err) => {
      if (err.response) {
        if (err.response.status === 404) {
          history.push('/lobbies/');
        }
      }
    });
  }, [roomId]);
  useEffect(() => {
    const gameStateCallback = (data) => {
      console.log(data);
      setStates((curStates) => (
        sortByEpoch([...curStates, data])
      ));
    };
    const gsSocket = socketio.on('gamestate', gameStateCallback);
    const joinedCallback = (data) => {
      console.log(data);
      setRoom((currRoom) => ({
        ...currRoom,
        players: [...currRoom.players, {
          gamerole: data.gamerole, id: data.playerid, name: data.name,
        }],
      }));
    };
    const jnSocket = socketio.on('joined', joinedCallback);
    socketio.emit('spectate', { roomid: roomId }, (_, data) => {
      if (data.states) {
        const localStates = sortByEpoch(data.states);
        setStates(localStates);
      }
    });

    function cleanup() {
      gsSocket.off('gamestate', gameStateCallback);
      jnSocket.off('joined', joinedCallback);
    }

    return cleanup;
  }, [roomId, room.game]);
  const state = epoch === null ? states[states.length - 1] : states[epoch];
  const board = state ? state.board : null;
  const Game = Games[room.game] || Games.Default;
  return (
    <>
      <div className={classes.mainArea}>
        <Container className={classes.mainArea}>
          <Typography component="h5" variant="h5">
            Asimov&apos;s Playground
          </Typography>
          <Typography variant="h6">
            {`Spectating ${room.name}`}
          </Typography>
          <span>
State:
            <Chip
              label={capitalize(room.status)}
              style={{ backgroundColor: getColor(room.status) }}
            />
          </span>
          {board && Game ? <Game board={board} /> : (<Typography variant="body2">Game not started</Typography>)}
          <MobileStepper
            className={classes.stepper}
            variant="text"
            backButton={(
              <div>
                <Button
                  size="small"
                  onClick={() => {
                    setEpoch(0);
                  }}
                  disabled={epoch === 0 || states.length === 0}
                >
                  <FirstPage />
                  First
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    setEpoch(epoch === null ? states.length - 2 : epoch - 1);
                  }}
                  disabled={epoch === 0 || states.length === 0}
                >
                  <KeyboardArrowLeft />
                  Back
                </Button>
              </div>
            )}
            nextButton={(
              <div>
                <Button
                  size="small"
                  onClick={() => {
                    setEpoch(epoch === states.length - 2 ? null : epoch + 1);
                  }}
                  disabled={epoch === null || epoch === states.length - 1}
                >
                  Next
                  <KeyboardArrowRight />
                </Button>
                <Button
                  size="small"
                  onClick={() => {
                    setEpoch(states.length - 1);
                  }}
                  disabled={epoch === null || epoch === states.length - 1}
                >
                  Last
                  <LastPage />
                </Button>
              </div>
            )}
            steps={states.length}
            activeStep={epoch === null ? states.length - 1 : epoch}
          />
        </Container>
      </div>
      <Drawer variant="permanent" anchor="right" className={classes.playerDrawer}>
        <Container className={classes.playerDrawerInner}>
          <Typography variant="subtitle2">Players</Typography>
          {room.players ? (
            <List>
              {room.players.map((player) => (
                <ListItem key={player.id}>
                  <ListItemText primary={player.gamerole ? `${player.name} (${player.gamerole})` : player.name} />
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
  match: PropTypes.shape({
    params: PropTypes.shape({ roomId: PropTypes.string.isRequired }),
  }).isRequired,
};
export default Spectate;
