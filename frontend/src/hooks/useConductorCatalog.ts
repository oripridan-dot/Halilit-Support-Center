import { useQuery } from '@tanstack/react-query';
import {
  CATALOG_ENDPOINT,
  ConductorProduct,
  ConductorCatalogResponse,
  PaginatedCatalogResponse,
} from './implement_backend_pagination_for_catalog_data_in_useconducto.schema';

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
}: UseConductorCatalogProps): ConductorCatalogResponse => {
  const queryKey = [
    'conductorCatalog',
    page,
    pageSize,
    searchQuery,
    sortBy,
    category,
    brand,
  ];

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<PaginatedCatalogResponse, any>({
    queryKey,
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        pageSize: pageSize.toString(),
        searchQuery,
        sortBy,
        category,
        brand,
      });
      const url = `${CATALOG_ENDPOINT}?${params.toString()}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const jsonData: ConductorCatalogResponse = await response.json();

      if (!jsonData || !jsonData.data || !jsonData.data.products || jsonData.data.totalItems === undefined || jsonData.data.totalPages === undefined || jsonData.data.currentPage === undefined || jsonData.data.pageSize === undefined) {
          throw new Error("Invalid data format from API");
      }

      return jsonData.data;
    },
    retry: (failureCount, error) => {
        if (error && (error.message.includes('500') || error.message.includes('503'))) {
            return failureCount < 3;
        }
        return false;
    },
  });

  return {
    data: data || { products: [], totalItems: 0, totalPages: 0, currentPage: 1, pageSize: 25 },
    isLoading,
    error,
    refetch,
  };
};

export default useConductorCatalog;