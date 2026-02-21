import { useState, useMemo } from 'react';
import { useQuery, keepPreviousData } from '@tanstack/react-query';
import {
  CATALOG_ENDPOINT,
  CatalogRequestParams,
  PaginatedCatalogResponse,
  ConductorProduct,
} from './implement_backend_pagination_for_catalog_data_in_useconducto.schema';

export type { ConductorProduct, PaginatedCatalogResponse, CatalogRequestParams };

interface UseConductorCatalogParams extends CatalogRequestParams {
  enabled?: boolean;
}

export const useConductorCatalog = (params: UseConductorCatalogParams = {}) => {
  const [page, setPage] = useState<number>(params.page ?? 1);
  const [pageSize, setPageSize] = useState<number>(params.pageSize ?? 25);
  const [sortBy, setSortBy] = useState<string>(params.sortBy ?? '');

  const queryParams = useMemo(
    () => ({
      page,
      pageSize,
      searchQuery: params.searchQuery ?? '',
      sortBy,
      category: params.category ?? '',
      brand: params.brand ?? '',
    }),
    [page, pageSize, params.searchQuery, sortBy, params.category, params.brand],
  );

  const { data, isLoading, error, refetch } = useQuery<PaginatedCatalogResponse, Error>({
    queryKey: ['conductorCatalog', queryParams],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (queryParams.page) searchParams.append('page', String(queryParams.page));
      if (queryParams.pageSize) searchParams.append('pageSize', String(queryParams.pageSize));
      if (queryParams.searchQuery) searchParams.append('searchQuery', queryParams.searchQuery);
      if (queryParams.sortBy) searchParams.append('sortBy', queryParams.sortBy);
      if (queryParams.category) searchParams.append('category', queryParams.category);
      if (queryParams.brand) searchParams.append('brand', queryParams.brand);

      const url = `${CATALOG_ENDPOINT}?${searchParams.toString()}`;
      const response = await fetch(url, { headers: { Accept: 'application/json' } });
      if (!response.ok) {
        throw new Error(`Catalog fetch failed ${response.status}: ${response.statusText}`);
      }
      return response.json() as Promise<PaginatedCatalogResponse>;
    },
    placeholderData: keepPreviousData,
    enabled: params.enabled !== false,
  });

  return {
    products: data?.products ?? [],
    totalItems: data?.totalItems ?? 0,
    totalPages: data?.totalPages ?? 0,
    currentPage: data?.currentPage ?? 1,
    pageSize: data?.pageSize ?? pageSize,
    isLoading,
    error,
    refetch,
    setPage,
    setPageSize,
    setSortBy,
  };
};

export default useConductorCatalog;
