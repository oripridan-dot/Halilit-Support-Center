import { useQuery } from 'react-query';
import {
  CATALOG_ENDPOINT,
  CatalogRequestParams,
  PaginatedCatalogResponse,
  ConductorProduct,
import { fetcher } from './utils/fetcher';

interface UseConductorCatalogParams extends CatalogRequestParams {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

export const useConductorCatalog = (params: UseConductorCatalogParams = {}) => {
  const { page = 1, pageSize = 25, searchQuery = '', sortBy = '', category = '', brand = '' } = params;

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<PaginatedCatalogResponse, Error>(
    ['conductorCatalog', page, pageSize, searchQuery, sortBy, category, brand],
    () =>
      fetcher(CATALOG_ENDPOINT, {
        page,
        pageSize,
        searchQuery,
        sortBy,
        category,
        brand,
      }),
    {
      keepPreviousData: true,
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
    itemsPerPage,
    isLoading,
    error,
    refetch,
  };
};