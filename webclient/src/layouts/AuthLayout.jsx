import React from 'react';
import { Grid, CssBaseline, Paper } from '@material-ui/core';

import useStyles from '../components/Auth/styles';

const AuthLayout = ({ children }) => {
  const classes = useStyles();
  return (
    <Grid container component="main" className={classes.root}>
      <CssBaseline />
      <Grid item xs={false} sm={4} md={7} className={classes.image} />
      <Grid item xs={12} sm={8} md={5} component={Paper} elevation={6} square>
        <div className={classes.paper}>
          {children}
        </div>
      </Grid>
    </Grid>
  );
};

export default AuthLayout;
