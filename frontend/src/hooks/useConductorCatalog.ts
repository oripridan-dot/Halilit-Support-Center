import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';

import { useState } from 'react';

export const useConductorCatalog = (
  initialPage: number = 1,
  initialPageSize: number = 25,
  initialSearchQuery: string = '',
  initialSortBy: string = '',
  initialCategory: string = '',
  initialBrand: string = ''
) => {
  const [searchParams] = useSearchParams();

  const page = parseInt(searchParams.get('page') || initialPage.toString(), 10);
  const pageSize = parseInt(searchParams.get('pageSize') || initialPageSize.toString(), 10);
  const searchQuery = searchParams.get('searchQuery') || initialSearchQuery;
  const sortBy = searchParams.get('sortBy') || initialSortBy;
  const category = searchParams.get('category') || initialCategory;
  const brand = searchParams.get('brand') || initialBrand;

  const params: CatalogParams = {
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
  } = useQuery<CatalogResponse, Error>({
    queryKey: ['catalog', params],
    queryFn: async () => {
      const response = await fetch(`${CATALOG_ENDPOINT}?${new URLSearchParams(
        Object.entries(params)
          .filter(([, value]) => value !== '' && value !== undefined && value !== null)
          .map(([key, value]) => [key, value?.toString()])
      )}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json() as Promise<CatalogResponse>;
    },
    keepPreviousData: true,
  });

  return {
    products: data?.products || [],
    totalItems: data?.totalItems || 0,
    totalPages: data?.totalPages || 0,
    currentPage: data?.currentPage || 1,
    pageSize: data?.pageSize || 25,
    isLoading,
    error,
    refetch,
    loadingComponent: isLoading ? <ResearchAnimation brandName="Halilit" brandColor="#0ea5e9" /> : null,
  };
};