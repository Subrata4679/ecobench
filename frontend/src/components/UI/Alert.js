import React from 'react';

export const Alert = ({ children, variant = 'info', className = '', ...props }) => {
  const variants = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    error: 'bg-red-50 border-red-200 text-red-800'
  };
  
  return (
    <div 
      className={`border rounded-md p-4 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};

export const AlertDescription = ({ children, className = '', ...props }) => {
  return (
    <div 
      className={`text-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
