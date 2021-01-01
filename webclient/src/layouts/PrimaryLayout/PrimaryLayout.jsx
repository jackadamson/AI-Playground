import React, { useState } from 'react';
import { Redirect, Route, Switch } from 'react-router';
import classNames from 'classnames';
import DashboardIcon from '@material-ui/icons/Dashboard';
import BubbleChart from '@material-ui/icons/BubbleChart';
import Person from '@material-ui/icons/Person';

import Attribution from '../../components/Attribution';
import Lobbies from '../../components/Lobbies';
import Sidebar from '../../components/Sidebar';
import Spectate from '../../components/Spectate';
import useStyles from './styles';

const routes = [
  {
    path: '/lobbies',
    name: 'Lobbies',
    icon: BubbleChart,
    component: Lobbies,
    link: true,
  },
  {
    path: '/profile',
    name: 'Profile',
    icon: Person,
    component: Lobbies,
    link: true,
  },
  {
    path: '/spectate/:roomId',
    link: false,
    icon: Person,
    name: 'Spectate',
    component: Spectate,
  },
  {
    href: '/api/v1/docs',
    name: 'API Docs',
    icon: DashboardIcon,
    link: true,
  },
];

const switchRoutes = (
  <Switch>
    {routes.filter(({ path }) => (!!path)).map((prop) => (
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
  const [collapsed, setCollapsed] = useState(true);

  return (
    <div className={classes.wrapper}>
      <Sidebar routes={routes} collapsed={collapsed} setCollapsed={setCollapsed} />
      <div className={classNames(
        classes.mainPanel,
        collapsed ? classes.collapsedMainPanel : classes.openMainPanel,
      )}
      >
        <div className={classes.content}>
          <div className={classes.container}>{switchRoutes}</div>
          <Attribution />
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
