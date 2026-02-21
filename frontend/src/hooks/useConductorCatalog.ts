import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';

interface UseConductorCatalogProps {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

const defaultPageSize = 25;

const useConductorCatalog = ({
  page = 1,
  pageSize = defaultPageSize,
  searchQuery = '',
  sortBy = '',
  category = '',
  brand = '',
}: UseConductorCatalogProps = {}) => {
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
    error,
    refetch,
  } = useQuery<PaginatedCatalogResponse, Error>(
    ['conductorCatalog', params],
    async () => {
      const url = new URL(CATALOG_ENDPOINT, window.location.origin);
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          url.searchParams.append(key, String(value));
        }
      });

      const response = await fetch(url.toString());

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json() as Promise<PaginatedCatalogResponse>;
    },
  );

  const products = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const currentPageSize = data?.pageSize || defaultPageSize;

  return {
    products,
    totalItems,
    totalPages,
    currentPage,
    pageSize: currentPageSize,
    isLoading,
    error: error ? (error as Error).message : null,
    retry: refetch,
  };
};

export default useConductorCatalog;