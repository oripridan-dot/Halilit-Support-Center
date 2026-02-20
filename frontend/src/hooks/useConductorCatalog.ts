import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';

interface UseConductorCatalogProps {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  initialCfpFilter?: string;
}

const defaultPageSize = 25;

const fetchCatalogData = async (page: number, pageSize: number, searchQuery?: string, initialCfpFilter?: string): Promise<PaginatedCatalogResponse> => {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
  });

  if (searchQuery) {
    params.append('searchQuery', searchQuery);
  }

  if (initialCfpFilter) {
    params.append('cfpFilter', initialCfpFilter);
  }

  const url = `${CATALOG_ENDPOINT}?${params.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch catalog data: ${response.status}`);
  }

  return response.json() as Promise<PaginatedCatalogResponse>;
};

const useConductorCatalog = ({ page = 1, pageSize = defaultPageSize, searchQuery, initialCfpFilter }: UseConductorCatalogProps = {}) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<PaginatedCatalogResponse, Error>(
    ['catalog', page, pageSize, searchQuery, initialCfpFilter],
    () => fetchCatalogData(page, pageSize, searchQuery, initialCfpFilter),
    {
      keepPreviousData: true,
    }
  );

  useEffect(() => {
    if (searchQuery !== undefined || initialCfpFilter !== undefined) {
      refetch();
    }
  }, [searchQuery, initialCfpFilter, refetch]);


  return {
    products: data?.products || [],
    totalItems: data?.totalItems || 0,
    totalPages: data?.totalPages || 0,
    currentPage: data?.currentPage || page,
    pageSize: data?.pageSize || pageSize,
    isLoading,
    error,
    refetch,
  };
};

export default useConductorCatalog;