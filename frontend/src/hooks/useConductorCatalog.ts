import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import {
  CONDUCTOR_CATALOG_ENDPOINT,
  ConductorProduct,
  ConductorCatalogParams,
  PaginatedCatalogResponse,

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
  const [error, setError] = useState<Error | null>(null);

  const params: ConductorCatalogParams = {
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
  } = useQuery<PaginatedCatalogResponse, Error>(
    ['catalog', params],
    async () => {
      const queryParams = new URLSearchParams();
      if (params.page !== undefined) queryParams.append('page', String(params.page));
      if (params.pageSize !== undefined) queryParams.append('pageSize', String(params.pageSize));
      if (params.searchQuery) queryParams.append('searchQuery', params.searchQuery);
      if (params.sortBy) queryParams.append('sortBy', params.sortBy);
      if (params.category) queryParams.append('category', params.category);
      if (params.brand) queryParams.append('brand', params.brand);

      const url = `${CONDUCTOR_CATALOG_ENDPOINT}?${queryParams.toString()}`;
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json() as Promise<PaginatedCatalogResponse>;
    },
    {
      onError: (err: Error) => {
        setError(err);
      },
    }
  );

  const products = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const itemsPerPage = data?.pageSize || 25;

  return {
    products,
    totalItems,
    totalPages,
    currentPage,
    pageSize: itemsPerPage,
    isLoading,
    isError: isError || !!error,
    error,
  };
};

export default useConductorCatalog;