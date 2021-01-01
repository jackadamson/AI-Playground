import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import PropTypes from 'prop-types';
import JSONPretty from 'react-json-pretty';
import { Paper } from '@material-ui/core';
import 'react-json-pretty/themes/monikai.css';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    backgroundColor: theme.palette.background.paper,
    fontSize: '1.25rem',
  },
}));
const Default = ({ board }) => {
  const classes = useStyles();
  return (
    <Paper className={classes.root} elevation={4}>
      <JSONPretty id="json-pretty" data={board} />
    </Paper>
  );
};
Default.propTypes = {
  board: PropTypes.shape({ grid: PropTypes.arrayOf(PropTypes.array) }).isRequired,
};

export default Default;
