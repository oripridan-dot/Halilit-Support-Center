import { useQuery } from '@tanstack/react-query';
import { CATALOG_ENDPOINT, ConductorProduct, PaginatedCatalogResponse, ConductorCatalogResponse } from '../hooks/implement_backend_pagination_for_catalog_data_in_useconducto.schema';

interface UseConductorCatalogParams {
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
}: UseConductorCatalogParams = {}) => {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: String(pageSize),
    searchQuery,
    sortBy,
    category,
    brand,
  });

  const url = `${CATALOG_ENDPOINT}?${params.toString()}`;

  const { data, isLoading, error, refetch } = useQuery<ConductorCatalogResponse, Error>(
    ['conductorCatalog', page, pageSize, searchQuery, sortBy, category, brand],
    async () => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json() as Promise<ConductorCatalogResponse>;
    }
  );

  const products = data?.data?.products || [];
  const totalItems = data?.data?.totalItems || 0;
  const totalPages = data?.data?.totalPages || 0;
  const currentPage = data?.data?.currentPage || 1;
  const currentPageSize = data?.data?.pageSize || 25;

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