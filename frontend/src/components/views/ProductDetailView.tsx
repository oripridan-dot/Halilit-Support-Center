import React, { useState, useEffect } from 'react';
import { Product } from '../../types';
import { Copy } from 'lucide-react';

interface Props {
  product: Product | undefined;
}

const ProductDetailView: React.FC<Props> = ({ product }) => {
  const [copyStatus, setCopyStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    if (copyStatus !== 'idle') {
      const timeout = setTimeout(() => {
        setCopyStatus('idle');
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [copyStatus]);

  const handleCopySku = async () => {
    if (!product?.id) return;
    try {
      await navigator.clipboard.writeText(product.id);
      setCopyStatus('success');
    } catch (err) {
      console.error('Failed to copy SKU: ', err);
      setCopyStatus('error');
    }
  };

  const shouldShowCopyButton = product?.price === null || product?.price === 0;

  return (
    <div>
      {/* Product Detail Content */}
      {product && (
        <>
          <div className="flex items-center space-x-2 mb-2">
            <span className="font-semibold">SKU:</span>
            <span>{product.id}</span>
            {shouldShowCopyButton && (
              <button
                onClick={handleCopySku}
                className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Copy className="mr-1 h-4 w-4" />
                {copyStatus === 'success'
                  ? 'Copied!'
                  : copyStatus === 'error'
                  ? 'Copy Failed'
                  : 'Copy SKU'}
              </button>
            )}
          </div>
          {/* Price Display */}
          <div className="mb-4">
            {product.price === null || product.price === 0 ? (
              <span>Price on request</span>
            ) : (
              <span>{product.pricing?.price_il} ILS</span>
            )}
          </div>
          {copyStatus === 'error' && (
            <div className="text-red-500 text-sm">
              Copy failed. Please copy the SKU manually.
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ProductDetailView;