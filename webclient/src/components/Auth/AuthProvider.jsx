import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Login from './Login';

export const AuthContext = React.createContext({});

const AuthProvider = ({ children }) => {
  const [token, setToken] = useState('');
  // States: authenticated, unauthenticated, refreshing, authrequired
  const [authState, setAuthState] = useState('unauthenticated');

  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [roles, setRoles] = useState([]);

  const logout = () => {
    axios.post('/auth/logout')
      .then(() => {
        setToken('');
        setAuthState('unauthenticated');
      });
  };
  useEffect(() => {
    if (authState === 'unauthenticated') {
      setAuthState('refreshing');
      axios.post('/auth/refresh')
        .then((resp) => {
          if (resp.data.success) {
            setToken(resp.data.payload);
            setAuthState('authenticated');
          }
        })
        .catch(() => {
          setAuthState('authrequired');
        });
    }
  }, [authState]);
  useEffect(() => {
    axios.defaults.headers.common.Authorization = token ? `Bearer ${token}` : '';
  }, [token]);
  useEffect(() => {
    axios.get('/auth/me')
      .then((resp) => {
        setEmail(resp.data.email);
        setUsername(resp.data.username);
        setRoles(resp.data.roles);
      });
  }, [token]);
  return (
    <AuthContext.Provider value={{
      logout, email, username, roles,
    }}
    >
      {authState === 'authenticated' ? children : (
        <Login
          authState={authState}
          setAuthState={setAuthState}
          setToken={setToken}
        />
      )}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
