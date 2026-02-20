import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import ImageWithFallback from '../../components/ImageWithFallback';
import { useSearchParams } from 'react-router-dom';

const fetchCatalogData = async (params: CatalogRequestParams): Promise<PaginatedCatalogResponse> => {
  const { page = 1, pageSize = 25, searchQuery = '', sortBy = '', category = '', brand = '' } = params;
  const url = new URL(CATALOG_ENDPOINT, window.location.origin);
  Object.entries({ page, pageSize, searchQuery, sortBy, category, brand })
    .filter(([, value]) => value !== '' && value !== undefined)
    .forEach(([key, value]) => {
      url.searchParams.append(key, String(value));
    });

  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json() as Promise<PaginatedCatalogResponse>;
};

const useConductorCatalog = (
  page: number = 1,
  pageSize: number = 25,
  searchQuery: string = '',
  sortBy: string = '',
  category: string = '',
  brand: string = '',
) => {
  const params: CatalogRequestParams = {
    page,
    pageSize,
    searchQuery,
    sortBy,
    category,
    brand,
  };

  const { data, isLoading, isError, error, refetch } = useQuery<PaginatedCatalogResponse, Error>({
    queryKey: ['catalog', params],
    queryFn: () => fetchCatalogData(params),
    keepPreviousData: true,
  });

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
    pageSize: itemsPerPage,
    isLoading,
    isError,
    error,
    refetch,
  };
};

interface CatalogGridProps {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

const CatalogGrid: React.FC<CatalogGridProps> = ({ page, pageSize, searchQuery, sortBy, category, brand }) => {
  const { products, isLoading, isError, error, totalPages, currentPage, refetch, pageSize: itemsPerPage } = useConductorCatalog(
    page,
    pageSize,
    searchQuery,
    sortBy,
    category,
    brand,
  );
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const newParams = new URLSearchParams();
    if (page && page !== 1) newParams.set('page', String(page));
    if (pageSize && pageSize !== 25) newParams.set('pageSize', String(pageSize));
    if (searchQuery) newParams.set('searchQuery', searchQuery);
    if (sortBy) newParams.set('sortBy', sortBy);
    if (category) newParams.set('category', category);
    if (brand) newParams.set('brand', brand);

    setSearchParams(newParams);
  }, [page, pageSize, searchQuery, sortBy, category, brand, setSearchParams]);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
        {[...Array(itemsPerPage)].map((_, index) => (
          <div key={index} className="bg-zinc-700 rounded-md shadow-md overflow-hidden">
            <div className="bg-zinc-800 h-48 w-full"></div>
            <div className="p-4">
              <div className="bg-zinc-700 h-6 w-3/4 mb-2 rounded-md"></div>
              <div className="bg-zinc-700 h-4 w-1/2 rounded-md"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4 text-red-500 dark:text-red-400">
        Error: {error?.message}
        <button onClick={refetch} className="ml-2 px-2 py-1 bg-zinc-600 hover:bg-zinc-500 rounded-md">
          Retry
        </button>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="p-4 text-zinc-300">
        No products found.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-4">
      {products.map((product) => (
        <div key={product.id} className="bg-zinc-800 rounded-md shadow-md overflow-hidden">
          <ImageWithFallback
            src={product.image_url}
            alt={product.name}
            fallbackSrc="/placeholder.png"
            className="w-full h-48 object-cover"
          />
          <div className="p-4">
            <h3 className="text-zinc-200 text-lg font-medium truncate">{product.name}</h3>
            <p className="text-zinc-400 text-sm truncate">{product.brand} - {product.category}</p>
            <p className="text-zinc-100 font-bold mt-2">${product.price.toFixed(2)}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CatalogGrid;
export { useConductorCatalog };