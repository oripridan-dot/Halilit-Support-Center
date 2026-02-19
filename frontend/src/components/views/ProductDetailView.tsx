import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { AsyncResult, createAsyncResult } from '../../lib/communicationProtocol';
import { Accessory } from '../../types';
import Image from 'next/image';
import Link from 'next/link';

interface AccessoryProduct {
  id: number;
  name: string;
  imageUrl: string;
  price: number | null;
}

interface AccessoryRecommendationsProps {
  productId: number;
}


const fetchAccessories = async (productId: number): Promise<AccessoryProduct[] | null> => {
    try {
        const response = await fetch(`/api/v1/products/${productId}/accessories`);
        if (response.ok) {
            if (response.status === 204) {
                return [];
            }
            const data = await response.json();
            return data.accessories;
        } else {
            console.error('Failed to fetch accessories', response.status);
            return null;
        }
    } catch (error) {
        console.error('Error fetching accessories', error);
        return null;
    }
};

const AccessoryRecommendations: React.FC<AccessoryRecommendationsProps> = ({ productId }) => {
  const [accessoriesResult, setAccessoriesResult] = useState<AsyncResult<AccessoryProduct[], null>>(() =>
    createAsyncResult<AccessoryProduct[], null>({ state: 'idle' })
  );
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      setAccessoriesResult(prev => ({ ...prev, state: 'loading' }));
      const data = await fetchAccessories(productId);
      if (data === null) {
          setAccessoriesResult(prev => ({ ...prev, state: 'error', error: null })); // Generic error
      } else {
          setAccessoriesResult(prev => ({ ...prev, state: 'success', data }));
      }
    };

    fetchData();
  }, [productId]);

  const handleAccessoryClick = (accessoryId: number) => {
    router.push(`/products/${accessoryId}`);
  };


  if (accessoriesResult.state === 'loading') {
    return (
      <div className="py-4">
        <p className="text-sm text-gray-400">Loading accessories...</p>
      </div>
    );
  }

  if (accessoriesResult.state === 'error') {
    return (
      <div className="py-4 bg-red-100 border border-red-400 text-red-700 rounded p-2">
        <p className="text-sm">Failed to load accessory recommendations.</p>
      </div>
    );
  }

  if (accessoriesResult.state === 'success' && accessoriesResult.data && accessoriesResult.data.length === 0) {
    return (
      <div className="py-4 bg-amber-100 border border-amber-400 text-amber-700 rounded p-2">
        <p className="text-sm">No accessories found. Please check the product graph and add compatible accessories.</p>
      </div>
    );
  }

  if (accessoriesResult.state === 'success' && accessoriesResult.data) {
    return (
      <div className="py-4 overflow-x-auto whitespace-nowrap">
        <div className="flex space-x-4 pb-2">
          {accessoriesResult.data.map((accessory) => (
            <div
              key={accessory.id}
              className="inline-block w-48 rounded-lg shadow-md bg-slate-800 hover:bg-slate-700 transition-colors duration-200"
              onClick={() => handleAccessoryClick(accessory.id)}
              style={{ cursor: 'pointer' }}
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === 'Space') {
                  handleAccessoryClick(accessory.id);
                }
              }}
            >
              <div className="relative">
                  <Image
                      src={accessory.imageUrl || '/placeholder.png'}
                      alt={accessory.name}
                      width={192}
                      height={108}
                      className="rounded-t-lg object-cover"
                      layout="responsive"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/placeholder.png';
                      }}
                  />
              </div>
              <div className="p-2">
                <p className="text-sm font-medium text-white truncate">{accessory.name}</p>
                <p className="text-sm text-gray-300">
                  {accessory.price === null ? 'Call for Price' : `$${accessory.price.toFixed(2)}`}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return null;
};

export default AccessoryRecommendations;