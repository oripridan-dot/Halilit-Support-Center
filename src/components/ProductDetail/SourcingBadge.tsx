import React from 'react';
import { useQuery } from '@tanstack/react-query';

interface SourcingResponse {
  status: 'Ethically Sourced' | 'Partially Sourced' | 'Unknown Sourcing';
}

const SourcingBadge: React.FC<{ productId: string }> = ({ productId }) => {
  const { data, isLoading, error } = useQuery<SourcingResponse, Error>(
    ['sourcing', productId],
    async () => {
      const response = await fetch(`/api/products/${productId}/sourcing`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Product not found');
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to retrieve sourcing information.');
      }
      return response.json();
    }
  );

  if (isLoading) {
    return (
      <span className="bg-slate-700 text-white text-xs font-semibold mr-2 px-2.5 py-0.5 rounded">
        Loading...
      </span>
    );
  }

  if (error) {
    const errorMessage = error.message === 'Product not found' ? 'Sourcing information unavailable.' : error.message;

    return (
      <span className="bg-red-500 text-white text-xs font-semibold mr-2 px-2.5 py-0.5 rounded">
        {errorMessage}
      </span>
    );
  }

  if (!data) {
    return null;
  }

  let badgeText = '';
  let badgeStyle = '';

  switch (data.status) {
    case 'Ethically Sourced':
      badgeText = 'Ethically Sourced';
      badgeStyle = 'bg-green-500 text-white';
      break;
    case 'Partially Sourced':
      badgeText = 'Partially Sourced';
      badgeStyle = 'bg-yellow-500 text-slate-900';
      break;
    case 'Unknown Sourcing':
      badgeText = 'Unknown Sourcing';
      badgeStyle = 'bg-red-500 text-white';
      break;
  }

  return (
    <span className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${badgeStyle}`}>
      {badgeText}
    </span>
  );
};

export default SourcingBadge;