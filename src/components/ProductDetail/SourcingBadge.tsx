import React from 'react';
import { useQuery } from '@tanstack/react-query';

interface SourcingBadgeProps {
  productId: string;
}

const fetchSourcing = async (productId: string) => {
  const response = await fetch(`/products/${productId}/sourcing`);
  if (!response.ok) {
    const errorBody = await response.json();
    throw new Error(errorBody.detail || 'Failed to fetch sourcing information.');
  }
  return response.json();
};

const SourcingBadge: React.FC<SourcingBadgeProps> = ({ productId }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sourcing', productId],
    queryFn: () => fetchSourcing(productId),
  });

  if (isLoading) {
    return (
      <span className="inline-flex items-center rounded-full bg-zinc-700 px-2 py-0.5 text-xs font-medium text-zinc-300">
        Loading...
      </span>
    );
  }

  if (error) {
    return (
      <span className="inline-flex items-center rounded-full bg-red-500 px-2 py-0.5 text-xs font-medium text-white">
        Sourcing information unavailable.
      </span>
    );
  }

  const status = data?.status;

  if (!status) {
    return null;
  }

  let badgeText: string;
  let backgroundColorClass: string;
  let textColorClass: string;

  switch (status) {
    case 'Ethically Sourced':
      badgeText = 'Ethically Sourced';
      backgroundColorClass = 'bg-green-500';
      textColorClass = 'text-white';
      break;
    case 'Partially Sourced':
      badgeText = 'Partially Sourced';
      backgroundColorClass = 'bg-yellow-500';
      textColorClass = 'text-slate-900';
      break;
    case 'Unknown Sourcing':
      badgeText = 'Unknown Sourcing';
      backgroundColorClass = 'bg-red-500';
      textColorClass = 'text-white';
      break;
    default:
      badgeText = 'Unknown';
      backgroundColorClass = 'bg-red-500';
      textColorClass = 'text-white';
  }

  return (
    <span
      className={`inline-flex items-center rounded-full ${backgroundColorClass} px-2 py-0.5 text-xs font-medium ${textColorClass}`}
    >
      {badgeText}
    </span>
  );
};

export default SourcingBadge;