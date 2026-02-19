import React from 'react';

interface HalilitURLButtonProps {
  halilitUrl: string | null | undefined;
}

const HalilitURLButton: React.FC<HalilitURLButtonProps> = ({ halilitUrl }) => {
  if (!halilitUrl) {
    return null;
  }

  const handleClick = () => {
    if (halilitUrl) {
      window.open(halilitUrl, '_blank');
    }
  };

  const ariaLabel = `View on Halilit Website`;

  return (
    <button
      onClick={handleClick}
      className="bg-slate-900 hover:bg-blue-500 text-white font-medium py-2 px-4 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
      aria-label={ariaLabel}
    >
      View on Halilit Website
    </button>
  );
};

export default HalilitURLButton;