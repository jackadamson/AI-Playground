import React, { useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import LockOutlinedIcon from '@material-ui/icons/LockOutlined';
import {
  Button, Typography, Avatar, TextField,
} from '@material-ui/core';
import GridLoader from 'react-spinners/GridLoader';
import AuthLayout from '../../layouts/AuthLayout';
import useStyles from './styles';

const Login = ({ authState, setAuthState, setToken }) => {
  const classes = useStyles();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const login = (body) => {
    axios.post('/auth/login', body)
      .then((resp) => {
        if (resp.data.success) {
          setToken(resp.data.payload);
          setAuthState('authenticated');
        }
      })
      .catch((err) => {
      });
  };
  const doGuestLogin = () => {
    login({ guest: true });
  };
  const doLogin = (e) => {
    e.preventDefault();
    login({ email, password });
    return false;
  };
  return (
    <AuthLayout>
      {authState === 'refreshing' ? (
        <>
          <Avatar className={classes.avatar}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h5" variant="h5">
            Asimovs Playground
          </Typography>
          <Typography variant="subtitle2">
            Authenticating...
          </Typography>
          <GridLoader className={classes.spinner} />
        </>
      ) : (
        <>
          <Avatar className={classes.avatar}>
            <LockOutlinedIcon />
          </Avatar>
          <Typography component="h5" variant="h5">
            Asimovs Playground
          </Typography>
          <Typography variant="subtitle2">
            Login or use a guest account
          </Typography>
          <form className={classes.form} noValidate onSubmit={doLogin}>
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              id="email"
              label="Email Address"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              autoFocus
            />

            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
            <Button
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
              onClick={doLogin}
              type="submit"
            >
              Sign In
            </Button>
            <Button
              fullWidth
              variant="contained"
              color="secondary"
              className={classes.submit}
              onClick={doGuestLogin}
            >
              Sign In as Guest
            </Button>
          </form>
        </>
      )}
    </AuthLayout>
  );
};
Login.propTypes = {
  authState: PropTypes.string.isRequired,
  setAuthState: PropTypes.func.isRequired,
  setToken: PropTypes.func.isRequired,
};

export default Login;