import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import {
  CATALOG_ENDPOINT,
  CatalogRequestParams,
  PaginatedCatalogResponse,
  ConductorProduct,
} from '../hooks/implement_backend_pagination_for_catalog_data_in_useconducto.schema';

interface UseConductorCatalogProps {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

const useConductorCatalog = ({
  page = 1,
  pageSize = 25,
  searchQuery = '',
  sortBy = '',
  category = '',
  brand = '',
}: UseConductorCatalogProps) => {
  const [error, setError] = useState<string | null>(null);

  const params: CatalogRequestParams = {
    page,
    pageSize,
    searchQuery,
    sortBy,
    category,
    brand,
  };

  const {
    data,
    isLoading,
    isError,
  } = useQuery<PaginatedCatalogResponse, Error>({
    queryKey: ['catalog', params],
    queryFn: async () => {
      const url = new URL(CATALOG_ENDPOINT, window.location.origin);
      Object.entries(params).forEach(([key, value]) => {
        if (value !== '' && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
      const response = await fetch(url.toString());

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  const products: ConductorProduct[] = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const pageSize = data?.pageSize || 25;

  return {
    products,
    totalItems,
    totalPages,
    currentPage,
    pageSize,
    isLoading,
    isError,
    error,
  };
};

export default useConductorCatalog;