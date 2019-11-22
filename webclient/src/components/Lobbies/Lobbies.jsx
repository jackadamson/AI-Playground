import React, { useEffect, useState } from 'react';
import { Typography } from '@material-ui/core';
import axios from 'axios';
import useStyles from './styles';


const Lobbies = () => {
  const classes = useStyles();
  const [lobbies, setLobbies] = useState([]);
  useEffect(() => {
    axios.get('/rooms/').then((resp) => {
      setLobbies(resp.data);
    });
  }, []);
  return (
    <div className={classes.paper}>
      <Typography component="h5" variant="h5">
        Asimov's Playground
      </Typography>
      <Typography variant="subtitle2">
        Lobbies
      </Typography>
      <Typography variant="body2">
        {JSON.stringify(lobbies)}
      </Typography>
    </div>
  );
};

export default Lobbies;
