import React, { useEffect, useState } from 'react';
import { Typography } from '@material-ui/core';
import axios from 'axios';
import MaterialTable from 'material-table';
import MaterialTableIcons from '../MaterialTableIcons';
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
      />
    </div>
  );
};

export default Lobbies;
