import React from 'react';

export const Input = ({ 
  className = '', 
  type = 'text',
  ...props 
}) => {
  return (
    <input
      type={type}
      className={`block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${className}`}
      {...props}
    />
  );
};

export const Textarea = ({ 
  className = '', 
  rows = 3,
  ...props 
}) => {
  return (
    <textarea
      rows={rows}
      className={`block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 ${className}`}
      {...props}
    />
  );
};
