import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import { Typography } from '@material-ui/core';
import useStyles from './styles';


const Spectate = ({ match: { params: { roomId } } }) => {
  const classes = useStyles();
  return (
    <div className={classes.paper}>
      <Typography component="h5" variant="h5">
        Asimov's Playground
      </Typography>
      <Typography variant="body2">
        Spectate
      </Typography>
    </div>
  );
};
Spectate.propTypes = {
  match: PropTypes.shape({ params: PropTypes.shape({ roomId: PropTypes.string.isRequired }) }),
};
export default Spectate;
