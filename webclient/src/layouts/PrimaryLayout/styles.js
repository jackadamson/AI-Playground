import { makeStyles } from '@material-ui/core';
import {
  drawerWidthOpen,
  drawerWidthClosed,
  transition,
} from '../../assets/styles/commonStyles';

export default makeStyles((theme) => ({
  wrapper: {
    position: 'relative',
    top: '0',
    height: '100vh',
  },
  mainPanel: {
    backgroundColor: theme.palette.background.default,
    width: `calc(100% - ${drawerWidthOpen}px)`,
    overflow: 'auto',
    position: 'relative',
    float: 'right',
    ...transition,
    maxHeight: '100%',
    overflowScrolling: 'touch',
  },
  content: {
    padding: '30px 15px',
    minHeight: '100vh',
  },
  collapsedMainPanel: {
    width: `calc(100% - ${drawerWidthClosed}px)`,
  },
  openMainPanel: {
    width: `calc(100% - ${drawerWidthOpen}px)`,
  },
}));
