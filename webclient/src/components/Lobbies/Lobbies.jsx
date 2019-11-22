import React, { useState } from 'react';
import {
  Avatar, CssBaseline, Grid, Paper, Typography,
} from '@material-ui/core';
import LockOutlinedIcon from '@material-ui/core/SvgIcon/SvgIcon';
import useStyles from '../Auth/styles';


const Lobbies = () => {
  const classes = useStyles();
  const [lobbies, setLobbies] = useState([]);
  return (
    <div className={classes.paper}>
      <Avatar className={classes.avatar}>
        <LockOutlinedIcon />
      </Avatar>
      <Typography component="h5" variant="h5">
        Asimov's Playground
      </Typography>
      <Typography variant="subtitle2">
        Lobbies
      </Typography>
    </div>
  );
};

export default Lobbies;
