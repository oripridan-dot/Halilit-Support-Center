import { useQuery } from '@tanstack/react-query';
import { useState, useMemo } from 'react';

interface UseConductorCatalogProps {
  page?: number;
  pageSize?: number;
}

const defaultPageSize = 25;

export const useConductorCatalog = ({ page = 1, pageSize = defaultPageSize }: UseConductorCatalogProps = {}) => {
  const params: CatalogParams = { page, pageSize };

  const { data, isLoading, error, refetch } = useQuery<PaginatedCatalogResponse, Error>(
    ['catalog', params],
    () => fetcher<PaginatedCatalogResponse>(`${CATALOG_ENDPOINT}?page=${page}&pageSize=${pageSize}`),
  );

  const products = useMemo(() => data?.products || [], [data]);
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
    error,
    refetch,
  };
};