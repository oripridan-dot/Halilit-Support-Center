import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import {
  CATALOG_ENDPOINT,
  CatalogRequestParams,
  PaginatedCatalogResponse,
  ConductorProduct,
} from './implement_backend_pagination_for_catalog_data_in_useconducto.schema';

export type { ConductorProduct };

interface UseConductorCatalogProps {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

export const useConductorCatalog = ({
  page = 1,
  pageSize: pageSizeProp = 25,
  searchQuery = '',
  sortBy = '',
  category = '',
  brand = '',
}: UseConductorCatalogProps) => {
  const [error, setError] = useState<string | null>(null);

  const params: CatalogRequestParams = {
    page,
    pageSize: pageSizeProp,
    searchQuery,
    sortBy,
    category,
    brand,
  };

  const {
    data,
    isLoading,
    isError,
  } = useQuery<PaginatedCatalogResponse, Error>({
    queryKey: ['catalog', params],
    queryFn: async () => {
      const url = new URL(CATALOG_ENDPOINT, window.location.origin);
      Object.entries(params).forEach(([key, value]) => {
        if (value !== '' && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
      const response = await fetch(url.toString());

      if (!response.ok) {
        const msg = `HTTP error! status: ${response.status}`;
        setError(msg);
        throw new Error(msg);
      }
      return response.json();
    },
  });

  const products: ConductorProduct[] = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const pageSize = data?.pageSize || pageSizeProp;

  return {
    products,
    totalItems,
    totalPages,
    currentPage,
    pageSize,
    isLoading,
    isError,
    error,
  };
};

export default useConductorCatalog;

// ─── Stub hooks (awaiting implementation) ───────────────────────────────────
// These are re-exported from hooks/index.ts; stubs keep the barrel valid.

export const useProductsByGalaxy = (_galaxyId?: string) => ({
  products: [] as ConductorProduct[],
  isLoading: false,
  isError: false,
});

export const useProductsBySpectrum = (_spectrumId?: string) => ({
  products: [] as ConductorProduct[],
  isLoading: false,
  isError: false,
});

export const useProductRelationships = (_productId?: string) => ({
  relationships: [],
  isLoading: false,
  isError: false,
});

export const useProductFamily = (_familyId?: string) => ({
  family: null,
  isLoading: false,
  isError: false,
});

export const useProductVariants = (_productId?: string) => ({
  variants: [] as ConductorProduct[],
  isLoading: false,
  isError: false,
});

export const useConductorProductsByCategory = (_category?: string) => ({
  products: [] as ConductorProduct[],
  isLoading: false,
  isError: false,
});

export const useSpectrumStar = (_spectrumId?: string) => ({
  star: null,
  isLoading: false,
  isError: false,
});