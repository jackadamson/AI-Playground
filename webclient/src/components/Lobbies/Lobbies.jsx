import React, { useEffect, useState } from 'react';
import { Typography } from '@material-ui/core';
import axios from 'axios';
import MaterialTable from 'material-table';
import PlayArrowIcon from '@material-ui/icons/PlayArrow';
import PersonalVideoIcon from '@material-ui/icons/PersonalVideo';
import MaterialTableIcons from './MaterialTableIcons';
import MaterialTableAction from './MaterialTableAction';
import useStyles from './styles';


const Lobbies = () => {
  const classes = useStyles();
  const [lobbies, setLobbies] = useState([]);
  useEffect(() => {
    axios.get('/rooms/').then((resp) => {
      setLobbies(resp.data);
    });
  }, []);
  return (
    <div className={classes.paper}>
      <Typography component="h5" variant="h5">
        Asimov's Playground
      </Typography>

      <MaterialTable
        title="Lobbies"
        icons={MaterialTableIcons}
        columns={[
          { title: 'Name', field: 'name' },
          { title: 'Game', field: 'game' },
          { title: 'Status', field: 'status' },
          {
            title: 'Players',
            render: (rowData) => (
              `${rowData.players.length}/${rowData.maxplayers}`
            ),
          },
        ]}
        data={lobbies}
        actions={[
          { icon: PlayArrowIcon, tooltip: 'Join Lobby', base: '/play' },
          { icon: PersonalVideoIcon, tooltip: 'Spectate', base: '/spectate' },
        ]}
        components={{ Action: MaterialTableAction }}
        options={{
          actionsColumnIndex: -1,
          actionsCellStyle: {
            textAlign: 'center',
          },
        }}
      />
    </div>
  );
};

export default Lobbies;

