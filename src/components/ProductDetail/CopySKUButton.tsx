import React, { useState, useEffect } from 'react';

interface CopySKUButtonProps {
  sku: string;
}

const CopySKUButton: React.FC<CopySKUButtonProps> = ({ sku }) => {
  const [buttonText, setButtonText] = useState('Copy SKU');

  const copyToClipboard = async () => {
    if (!sku) {
      alert('Empty SKU: Cannot copy');
      return;
    }

    try {
      await navigator.clipboard.writeText(sku);
      setButtonText('Copied!');
      setTimeout(() => {
        setButtonText('Copy SKU');
      }, 2000);
    } catch (err) {
      setButtonText('Copy Failed');
      setTimeout(() => {
        setButtonText('Copy SKU');
      }, 2000);
    }
  };

  return (
    <button
      onClick={copyToClipboard}
      className="bg-slate-900 hover:bg-blue-500 text-white font-medium py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      {buttonText}
    </button>
  );
};

export default CopySKUButton;