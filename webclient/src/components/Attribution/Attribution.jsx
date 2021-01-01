import React from 'react';
import { Box, Link } from '@material-ui/core';

const Attribution = () => (
  <Box display="flex" justifyContent="center" mt={2}>
    <Box color="rgba(0, 0, 0, 0.6)">
      Fav Icon from
      {' '}
      <Link href="https://loading.io/icon/">loading.io</Link>
    </Box>
  </Box>
);

export default Attribution;
