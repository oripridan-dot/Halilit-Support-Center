import { useQuery } from '@tanstack/react-query';

const useConductorCatalog = (
  {
    page = 1,
    pageSize = 25,
    searchQuery = '',
    sortBy = '',
    category = '',
    brand = '',
  }: CatalogRequestParams = {}
) => {
  const params: CatalogRequestParams = {
    page,
    pageSize,
    searchQuery,
    sortBy,
    category,
    brand,
  };

  const { data, isLoading, error } = useQuery<PaginatedCatalogResponse, Error>(
    ['catalog', params],
    async () => {
      const queryParams = new URLSearchParams();
      if (page) queryParams.append('page', String(page));
      if (pageSize) queryParams.append('pageSize', String(pageSize));
      if (searchQuery) queryParams.append('searchQuery', searchQuery);
      if (sortBy) queryParams.append('sortBy', sortBy);
      if (category) queryParams.append('category', category);
      if (brand) queryParams.append('brand', brand);

      const url = `${CATALOG_ENDPOINT}?${queryParams.toString()}`;

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json() as Promise<PaginatedCatalogResponse>;
    }
  );

  const products = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const pageSize = data?.pageSize || 25;

  return {
    products,
    totalItems,
    totalPages,
    currentPage,
    pageSize,
    isLoading,
    error,
  };
};

export default useConductorCatalog;