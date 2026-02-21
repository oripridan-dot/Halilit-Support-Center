import { useQuery } from '@tanstack/react-query';

const CATALOG_ENDPOINT = '/api/conductor/catalog';

export interface ConductorProduct {
  id: string;
  name: string;
  brand: string;
  brand_logo?: string;
  galaxy_id?: string;
  spectrum_id?: string;
  category?: string;
  subcategory?: string;
  price?: number;
  price_eilat?: number;
  tier?: string;
  image_url?: string;
  image_gallery?: string[];
  description?: string;
  description_short?: string;
  specs?: Record<string, unknown>;
  features?: string[];
  rating?: number;
  review_count?: number;
  pros?: string[];
  cons?: string[];
  quality_score?: number;
  data_status?: string;
  data_missing?: string[];
  halilit_url?: string;
  official_url?: string;
  sources?: string[];
  family_id?: string | null;
  variant_key?: string | null;
  relationship_ids?: string[];
}

interface CatalogParams {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

interface CatalogApiResponse {
  products: ConductorProduct[];
  total?: number;
  totalItems?: number;
  totalPages?: number;
  currentPage?: number;
  pageSize?: number;
  brand_count?: number;
  indexes?: Record<string, unknown>;
}

async function fetchCatalog(params: CatalogParams): Promise<CatalogApiResponse> {
  const url = new URL(CATALOG_ENDPOINT, window.location.origin);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      url.searchParams.append(key, String(value));
    }
  });
  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Catalog fetch failed: HTTP ${response.status}`);
  }
  return response.json() as Promise<CatalogApiResponse>;
}

export function useConductorCatalog(params: CatalogParams = {}) {
  const { page = 1, pageSize = 250, searchQuery = '', sortBy = '', category = '', brand = '' } = params;

  const { data, isLoading, isError, error, refetch } = useQuery<CatalogApiResponse, Error>({
    queryKey: ['conductorCatalog', page, pageSize, searchQuery, sortBy, category, brand],
    queryFn: () => fetchCatalog({ page, pageSize, searchQuery, sortBy, category, brand }),
    staleTime: 5 * 60 * 1000,
    retry: 2,
  });

  return {
    products: data?.products ?? [],
    totalItems: data?.totalItems ?? data?.total ?? 0,
    totalPages: data?.totalPages ?? 1,
    currentPage: data?.currentPage ?? 1,
    pageSize: data?.pageSize ?? pageSize,
    isLoading,
    isError,
    error: error ? error.message : null,
    refetch,
  };
}