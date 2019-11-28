import React from 'react';
import { Router } from 'react-router';
import Auth from './components/Auth';
import PrimaryLayout from './layouts/PrimaryLayout/PrimaryLayout';
import history from './history';


export default function App() {
  return (
    <Router history={history}>
      <Auth>
        <PrimaryLayout />
      </Auth>
    </Router>
  );
}
