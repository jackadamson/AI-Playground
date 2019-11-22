import React from 'react';
import { Router } from 'react-router';
import { createBrowserHistory } from 'history';
import Auth from './components/Auth';
import PrimaryLayout from './layouts/PrimaryLayout/PrimaryLayout';

const history = createBrowserHistory();

export default function App() {
  return (
    <Router history={history}>
      <Auth>
        <PrimaryLayout />
      </Auth>
    </Router>
  );
}
