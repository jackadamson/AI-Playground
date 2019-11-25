import { makeStyles } from '@material-ui/core';

export default makeStyles((theme) => ({
  mainArea: {
    width: 'calc(100% - 200px)',
    height: '100%',
  },
  playerDrawer: {
    width: 240,
    flexShrink: 0,
    whiteSpace: 'nowrap',
  },
  playerDrawerInner: {
    paddingTop: 40,
    width: 200,
  },
}));
