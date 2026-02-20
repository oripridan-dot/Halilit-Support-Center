import { useQuery } from '@tanstack/react-query';
import {
  CONDUCTOR_CATALOG_ENDPOINT,
  PaginatedCatalogResponse,
  ConductorProduct,

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
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
    searchQuery,
    sortBy,
    category,
    brand,
  });

  const url = `${CONDUCTOR_CATALOG_ENDPOINT}?${params.toString()}`;

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<PaginatedCatalogResponse, any>({
    queryKey: ['conductorCatalog', page, pageSize, searchQuery, sortBy, category, brand],
    queryFn: async () => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    },
  });

  const products = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const currentPageSize = data?.pageSize || 25;

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

export default useConductorCatalog;