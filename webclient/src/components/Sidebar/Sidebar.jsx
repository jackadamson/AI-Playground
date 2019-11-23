import React, { useContext } from 'react';
import classNames from 'classnames';
import gravatar from 'gravatar';
import PropTypes from 'prop-types';
import { NavLink, useLocation } from 'react-router-dom';
import {
  List,
  ListItemAvatar,
  ListItem,
  ListItemText,
  Avatar,
  Drawer,
  Container,
  Typography,
} from '@material-ui/core';

import LockIcon from '@material-ui/icons/Lock';
import { AuthContext } from '../Auth/AuthProvider';
import useStyles from './styles';

const Sidebar = ({
  routes, collapsed, setCollapsed,
}) => {
  const classes = useStyles();
  const { email, username, logout } = useContext(AuthContext);
  const path = useLocation();

  const activeRoute = (routeName) => path.pathname.startsWith(routeName);
  const innerLink = (prop) => {
    const listItemClasses = classNames({
      [` ${classes.green}`]: activeRoute(prop.path),
    });
    return (
      <ListItem
        button
        className={classNames(
          collapsed ? classes.itemLinkNarrow : classes.itemLinkWide,
          classes.itemLink,
          listItemClasses,
        )}
        onClick={prop.onClick}
      >
        <prop.icon
          className={classes.itemIcon}
        />
        <ListItemText
          primary={prop.name}
          className={collapsed ? classes.hidden : classes.itemText}
          disableTypography
        />
      </ListItem>
    );
  };

  const links = (
    <>
      <List className={classes.list}>
        {routes.map((prop) => (prop.href ? (
          <a
            href={prop.href}
            className={classes.item}
            key={prop.name}
          >
            {innerLink(prop)}
          </a>
        ) : (
          <NavLink
            to={prop.path}
            className={classes.item}
            activeClassName="active"
            key={prop.name}
          >
            {innerLink(prop)}
          </NavLink>
        )))}
      </List>
      <Container className={classNames(
        classes.logoutOuter,
        collapsed ? classes.closed : classes.open,
      )}
      >
        <Typography
          className={classNames(classes.item, classes.logout)}
          component="span"
        >
          <ListItem
            button
            className={classNames(
              collapsed ? classes.itemLinkNarrow : classes.itemLinkWide,
              classes.itemLink,
            )}
          >
            <LockIcon
              className={classNames(classes.itemIcon)}
            />
            <ListItemText
              primary="Logout"
              className={collapsed ? classes.hidden : classes.itemText}
              disableTypography
            />
          </ListItem>
        </Typography>
      </Container>
    </>
  );
  const profile = (
    <div className={classes.logo}>
      <ListItem className={classes.logoInner}>
        <ListItemAvatar>
          <Avatar
            alt={email}
            src={gravatar.url(email, { r: 'pg', d: 'identicon' })}
          />
        </ListItemAvatar>
        <ListItemText
          primary={username}
          className={collapsed ? classes.hidden : classes.logoLink}
          disableTypography
        />
      </ListItem>
    </div>
  );
  return (
    <div>
      <Drawer
        anchor="left"
        variant="permanent"
        open
        classes={{
          paper: classNames(
            classes.drawerPaper,
            collapsed ? classes.drawerCollapsed : classes.drawerOpen,
          ),
        }}
      >
        {profile}
        <div className={classNames(
          classes.sidebarWrapper,
          collapsed ? classes.drawerCollapsed : classes.drawerOpen,
        )}
        >
          {links}
        </div>
        <div
          className={classes.background}
        />
      </Drawer>
    </div>
  );
};
Sidebar.propTypes = {
  routes: PropTypes.arrayOf(PropTypes.object).isRequired,
  collapsed: PropTypes.bool.isRequired,
  setCollapsed: PropTypes.func.isRequired,
};

export default Sidebar;
