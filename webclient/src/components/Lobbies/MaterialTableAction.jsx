import React from 'react';
import PropTypes from 'prop-types';

import IconButton from '@material-ui/core/IconButton';
import Tooltip from '@material-ui/core/Tooltip';
import { NavLink } from 'react-router-dom';

const MaterialTableAction = ({
  action: { base, icon: Icon, tooltip }, data: { id }, size, disabled,
}) => {
  const button = (
    <NavLink to={`${base}/${id}`}>
      <IconButton
        size={size}
        color="secondary"
        disabled={disabled}
      >
        <Icon />
      </IconButton>
    </NavLink>
  );
  return tooltip
    ? (
      <Tooltip title={tooltip}>
        {button}
      </Tooltip>
    ) : button;
};
MaterialTableAction.defaultProps = {
  data: {},
  disabled: false,
  size: 'medium',
};
MaterialTableAction.propTypes = {
  action: PropTypes.oneOfType([PropTypes.func, PropTypes.object]).isRequired,
  data: PropTypes.oneOfType([PropTypes.object, PropTypes.arrayOf(PropTypes.object)]),
  disabled: PropTypes.bool,
  size: PropTypes.string,
};
export default MaterialTableAction;
