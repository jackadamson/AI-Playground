import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import CrossIcon from '@material-ui/icons/Close';
import NaughtIcon from '@material-ui/icons/RadioButtonUnchecked';
import Grid from '@material-ui/core/Grid';
import PropTypes from 'prop-types';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    maxWidth: 360,
    backgroundColor: theme.palette.background.paper,
  },
  cell: {
    border: '2px solid #1e1e1e',
    textAlign: 'center',
    width: 120,
    height: 120,
    fontSize: 100,
  },
}));
const icons = { x: <CrossIcon fontSize="inherit" />, o: <NaughtIcon fontSize="inherit" /> };
const TicTacToe = ({ board: { grid } }) => {
  const classes = useStyles();
  return (
    <Grid container spacing={0}>
      {grid.flat().map((cell, idx) => (
        // eslint-disable-next-line react/no-array-index-key
        <Grid item key={idx} xs={4} className={classes.cell}>
          {icons[cell]}
        </Grid>
      ))}
    </Grid>
  );
};
TicTacToe.propTypes = {
  board: PropTypes.shape({ grid: PropTypes.arrayOf(PropTypes.array) }).isRequired,
};

export default TicTacToe;
