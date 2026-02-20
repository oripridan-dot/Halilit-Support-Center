import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import {
  CONDUCTOR_CATALOG_ENDPOINT,
  ConductorCatalogParams,
  ConductorProduct,
  PaginatedCatalogResponse,
import { ImageWithFallback } from '../components/ImageWithFallback';
import { useError } from './useError';

interface UseConductorCatalogProps {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

export const useConductorCatalog = ({
  page = 1,
  pageSize = 25,
  searchQuery = '',
  sortBy = '',
  category = '',
  brand = '',
}: UseConductorCatalogProps) => {
  const { handleError, error, resetError } = useError();
  const [retryCount, setRetryCount] = useState(0);
  const maxRetries = 3;

  const fetchCatalog = async (params: ConductorCatalogParams): Promise<PaginatedCatalogResponse> => {
    const url = new URL(CONDUCTOR_CATALOG_ENDPOINT, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        url.searchParams.append(key, String(value));
      }
    });

    try {
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json() as PaginatedCatalogResponse;
    } catch (fetchError: any) {
      handleError(fetchError);
      throw fetchError; // Re-throw to trigger react-query error
    }
  };


  const { data, isLoading, isError, refetch } = useQuery<PaginatedCatalogResponse, Error>({
    queryKey: [
      'conductorCatalog',
      page,
      pageSize,
      searchQuery,
      sortBy,
      category,
      brand,
    ],
    queryFn: () =>
      fetchCatalog({
        page,
        pageSize,
        searchQuery,
        sortBy,
        category,
        brand,
      }),
    onError: (err) => {
        console.error("Catalog fetch failed:", err);
    },
  });

  const handleRetry = () => {
    if (retryCount < maxRetries) {
      setRetryCount(prev => prev + 1);
      resetError();
      refetch();
    } else {
        console.error("Max retries reached.  Catalog fetch failed.");
    }
  };


  return {
    products: data?.products || [],
    totalItems: data?.totalItems || 0,
    totalPages: data?.totalPages || 0,
    currentPage: data?.currentPage || 1,
    pageSize: data?.pageSize || 25,
    isLoading,
    isError: isError || error !== null,
    error,
    refetch,
    handleRetry,
    retryCount,
  };
};

export const ConductorCatalogList = ({
  products,
  isLoading,
  isError,
  handleRetry,
  retryCount,
}: {
  products: ConductorProduct[];
  isLoading: boolean;
  isError: boolean;
  handleRetry: () => void;
  retryCount: number;
}) => {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 dark:bg-zinc-900 p-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index} className="animate-pulse dark:bg-zinc-800 rounded-lg p-4">
            <div className="h-40 bg-zinc-700 rounded-md mb-2"></div>
            <div className="h-4 bg-zinc-700 rounded-md mb-2"></div>
            <div className="h-4 bg-zinc-700 rounded-md"></div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="dark:bg-zinc-800 p-4 rounded-lg text-center">
        <p className="text-red-500">Failed to load catalog. Please try again.</p>
        <button
          onClick={handleRetry}
          className="mt-2 px-4 py-2 bg-zinc-700 text-white rounded hover:bg-zinc-600"
        >
          Retry ({retryCount}/{3})
        </button>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="dark:bg-zinc-800 p-4 rounded-lg text-center">
        <p>No products found.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 dark:bg-zinc-900 p-4">
      {products.map((product) => (
        <div key={product.id} className="dark:bg-zinc-800 rounded-lg shadow-md overflow-hidden">
          <ImageWithFallback
            src={product.image_url}
            alt={product.name}
            fallbackSrc="/placeholder.png"
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h3 className="text-lg font-semibold text-zinc-200 truncate">{product.name}</h3>
            <p className="text-zinc-400 text-sm truncate">{product.description}</p>
            <p className="text-zinc-300">${product.price.toFixed(2)}</p>
          </div>
        </div>
      ))}
    </div>
  );
};