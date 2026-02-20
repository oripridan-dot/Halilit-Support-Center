import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';

interface CopySKUButtonProps {
  sku: string;
  className?: string;
}

const CopySKUButton: React.FC<CopySKUButtonProps> = ({ sku, className = '' }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sku);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // fallback for browsers without clipboard API
      const el = document.createElement('textarea');
      el.value = sku;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <button
      onClick={handleCopy}
      title={`Copy SKU: ${sku}`}
      className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded
        bg-zinc-700 hover:bg-zinc-600 text-zinc-300 hover:text-white
        transition-colors duration-150 ${className}`}
    >
      {copied ? (
        <>
          <Check size={12} className="text-green-400" />
          <span className="text-green-400">Copied!</span>
        </>
      ) : (
        <>
          <Copy size={12} />
          <span>{sku}</span>
        </>
      )}
    </button>
  );
};

export { CopySKUButton };
export default CopySKUButton;
