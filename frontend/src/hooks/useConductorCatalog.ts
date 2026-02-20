import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import {
  CONDUCTOR_CATALOG_ENDPOINT,
  ConductorProduct,
  ConductorCatalogParams,
  PaginatedCatalogResponse,
import { ImageWithFallback } from './components/ImageWithFallback';

const useConductorCatalog = (params: ConductorCatalogParams = {}) => {
  const {
    page = 1,
    pageSize = 25,
    searchQuery = '',
    sortBy = '',
    category = '',
    brand = '',
  } = params;

  const [errorBannerVisible, setErrorBannerVisible] = useState(false);

  const fetchCatalog = async (
    page: number,
    pageSize: number,
    searchQuery: string,
    sortBy: string,
    category: string,
    brand: string
  ): Promise<PaginatedCatalogResponse> => {
    const url = new URL(CONDUCTOR_CATALOG_ENDPOINT, window.location.origin);
    const params = {
      page: page.toString(),
      pageSize: pageSize.toString(),
      searchQuery,
      sortBy,
      category,
      brand,
    };
    Object.keys(params).forEach(key => {
      if (params[key as keyof typeof params]) {
        url.searchParams.append(key, params[key as keyof typeof params]!);
      }
    });

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json() as Promise<PaginatedCatalogResponse>;
  };

  const { data, isLoading, error, refetch } = useQuery<PaginatedCatalogResponse, Error>({
    queryKey: [
      'conductorCatalog',
      page,
      pageSize,
      searchQuery,
      sortBy,
      category,
      brand,
    ],
    queryFn: () =>
      fetchCatalog(page, pageSize, searchQuery, sortBy, category, brand),
    onError: () => {
      setErrorBannerVisible(true);
    },
  });

  const products = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const pageSize = data?.pageSize || 25;

  const metadata = {
    totalItems,
    totalPages,
    currentPage,
    pageSize,
  };

  const handleRetry = () => {
    setErrorBannerVisible(false);
    refetch();
  };


  return {
    data: {
      products,
      metadata,
    },
    isLoading,
    error,
    refetch,
  };
};

export default useConductorCatalog;