import React, { useContext } from 'react';
import classNames from 'classnames';
import gravatar from 'gravatar';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import {
  List,
  ListItemAvatar,
  ListItem,
  ListItemText,
  Avatar,
  Icon,
  Drawer,
  Container,
  Typography,
} from '@material-ui/core';

import LockIcon from '@material-ui/icons/Lock';
import { AuthContext } from '../Auth/AuthProvider';
import useStyles from './styles';

const Sidebar = ({
  path, routes,
}) => {
  const classes = useStyles();
  const { email, username, logout } = useContext(AuthContext);

  function activeRoute(routeName) {
    return path === routeName;
  }

  const links = (
    <>
      <List className={classes.list}>
        {routes.map((prop) => {
          const listItemClasses = classNames({
            [` ${classes.green}`]: activeRoute(prop.layout + prop.path),
          });
          const whiteFontClasses = classNames({
            [` ${classes.whiteFont}`]: activeRoute(prop.layout + prop.path),
          });
          return prop.href ? (
            <a
              href={prop.href}
              className={classes.item}
              key={prop.name}
            >
              <ListItem button className={classes.itemLink + listItemClasses}>
                {typeof prop.icon === 'string' ? (
                  <Icon
                    className={classNames(classes.itemIcon, whiteFontClasses)}
                  >
                    {prop.icon}
                  </Icon>
                ) : (
                  <prop.icon
                    className={classNames(classes.itemIcon, whiteFontClasses)}
                  />
                )}
                <ListItemText
                  primary={prop.name}
                  className={classNames(classes.itemText, whiteFontClasses)}
                  disableTypography
                />
              </ListItem>
            </a>
          ) : (
            <NavLink
              to={prop.path}
              className={classes.item}
              activeClassName="active"
              key={prop.name}
            >
              <ListItem button className={classes.itemLink + listItemClasses}>
                {typeof prop.icon === 'string' ? (
                  <Icon
                    className={classNames(classes.itemIcon, whiteFontClasses)}
                  >
                    {prop.icon}
                  </Icon>
                ) : (
                  <prop.icon
                    className={classNames(classes.itemIcon, whiteFontClasses)}
                  />
                )}
                <ListItemText
                  primary={prop.name}
                  className={classNames(classes.itemText, whiteFontClasses)}
                  disableTypography
                />
              </ListItem>
            </NavLink>
          );
        })}
      </List>
      <Container className={classes.logoutOuter}>
        <Typography
          className={`${classes.item} ${classes.logout}`}
          component="span"
        >
          <ListItem button className={classes.itemLink} onClick={logout}>
            <LockIcon
              className={classNames(classes.itemIcon)}
            />
            <ListItemText
              primary="Logout"
              className={classes.itemText}
              disableTypography
            />
          </ListItem>
        </Typography>
      </Container>
    </>
  );
  const brand = (
    <div className={classes.logo}>
      <ListItem>
        <ListItemAvatar>
          <Avatar
            alt={email}
            src={gravatar.url(email, { r: 'pg', d: 'identicon' })}
          />
        </ListItemAvatar>
        <ListItemText primary={username} className={classes.logoLink} disableTypography />
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
          paper: classes.drawerPaper,
        }}
      >
        {brand}
        <div className={classes.sidebarWrapper}>
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
  path: PropTypes.string.isRequired,
  routes: PropTypes.array.isRequired,
};

export default Sidebar;
