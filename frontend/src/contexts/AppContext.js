import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};

// Initial state
const initialState = {
  notifications: [],
  loading: false,
  selectedOrganization: null,
  selectedKPI: null,
  selectedPeriod: '2023',
  sidebarOpen: false,
};

// Action types
const actionTypes = {
  SET_LOADING: 'SET_LOADING',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  SET_SELECTED_ORGANIZATION: 'SET_SELECTED_ORGANIZATION',
  SET_SELECTED_KPI: 'SET_SELECTED_KPI',
  SET_SELECTED_PERIOD: 'SET_SELECTED_PERIOD',
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  SET_SIDEBAR_OPEN: 'SET_SIDEBAR_OPEN',
};

// Reducer
const appReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case actionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, {
          id: Date.now(),
          ...action.payload
        }]
      };
    
    case actionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter(n => n.id !== action.payload)
      };
    
    case actionTypes.SET_SELECTED_ORGANIZATION:
      return { ...state, selectedOrganization: action.payload };
    
    case actionTypes.SET_SELECTED_KPI:
      return { ...state, selectedKPI: action.payload };
    
    case actionTypes.SET_SELECTED_PERIOD:
      return { ...state, selectedPeriod: action.payload };
    
    case actionTypes.TOGGLE_SIDEBAR:
      return { ...state, sidebarOpen: !state.sidebarOpen };
    
    case actionTypes.SET_SIDEBAR_OPEN:
      return { ...state, sidebarOpen: action.payload };
    
    default:
      return state;
  }
};

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Actions
  const setLoading = (loading) => {
    dispatch({ type: actionTypes.SET_LOADING, payload: loading });
  };

  const addNotification = (notification) => {
    dispatch({ type: actionTypes.ADD_NOTIFICATION, payload: notification });
    
    // Auto-remove after 5 seconds for success/info notifications
    if (notification.type === 'success' || notification.type === 'info') {
      setTimeout(() => {
        removeNotification(notification.id || Date.now());
      }, 5000);
    }
  };

  const removeNotification = (id) => {
    dispatch({ type: actionTypes.REMOVE_NOTIFICATION, payload: id });
  };

  const setSelectedOrganization = (organization) => {
    dispatch({ type: actionTypes.SET_SELECTED_ORGANIZATION, payload: organization });
  };

  const setSelectedKPI = (kpi) => {
    dispatch({ type: actionTypes.SET_SELECTED_KPI, payload: kpi });
  };

  const setSelectedPeriod = (period) => {
    dispatch({ type: actionTypes.SET_SELECTED_PERIOD, payload: period });
  };

  const toggleSidebar = () => {
    dispatch({ type: actionTypes.TOGGLE_SIDEBAR });
  };

  const setSidebarOpen = (open) => {
    dispatch({ type: actionTypes.SET_SIDEBAR_OPEN, payload: open });
  };

  // Utility functions
  const showSuccess = (message) => {
    addNotification({ type: 'success', message });
  };

  const showError = (message) => {
    addNotification({ type: 'error', message });
  };

  const showWarning = (message) => {
    addNotification({ type: 'warning', message });
  };

  const showInfo = (message) => {
    addNotification({ type: 'info', message });
  };

  const value = {
    ...state,
    setLoading,
    addNotification,
    removeNotification,
    setSelectedOrganization,
    setSelectedKPI,
    setSelectedPeriod,
    toggleSidebar,
    setSidebarOpen,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};
