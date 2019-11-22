import React, { useEffect, useState } from 'react';
import { Redirect, Route, Switch } from 'react-router';
import axios from 'axios';
import DashboardIcon from '@material-ui/icons/Dashboard';
import BubbleChart from '@material-ui/icons/BubbleChart';
import Person from '@material-ui/icons/Person';

import Sidebar from '../../components/Sidebar/Sidebar';
import useStyles from './styles';

import Lobbies from '../../components/Lobbies/Lobbies';

const routes = [
  {
    path: '/lobbies',
    name: 'Lobbies',
    icon: BubbleChart,
    component: Lobbies,
  },
  {
    path: '/profile',
    name: 'Profile',
    icon: Person,
    component: Lobbies,
  },
  {
    href: '/api/v1/',
    name: 'API Docs',
    icon: DashboardIcon,
  },
];

const switchRoutes = (
  <Switch>
    {routes.map((prop) => (
      <Route
        path={prop.path}
        component={prop.component}
        key={prop.name}
      />
    ))}
    <Route>
      <Redirect to="/lobbies" />
    </Route>
  </Switch>
);

const AuthLayout = () => {
  const classes = useStyles();

  return (
    <div className={classes.wrapper}>
      <Sidebar routes={routes} />
      <div className={classes.mainPanel}>
        <div className={classes.content}>
          <div className={classes.container}>{switchRoutes}</div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
