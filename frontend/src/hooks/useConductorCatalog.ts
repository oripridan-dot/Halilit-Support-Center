import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetcher } from '../utils/fetcher';
import { ResearchAnimation } from '../components/ResearchAnimation';
import { ImageWithFallback } from '../components/ImageWithFallback';
import { useValidateHeroImage } from './useValidateHeroImage';

// Define a lookup table for brand colors
const brandColors: { [key: string]: string } = {
  'Halilit': 'blue-500',
  'Brand2': 'green-500', // Example brand and color
  'Brand3': 'red-500', // Example brand and color
};

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
  pageSize = 25,
  searchQuery = '',
  sortBy = '',
  category = '',
  brand = '',
}: UseConductorCatalogProps) => {
  const params: CatalogRequestParams = {
    page,
    pageSize,
    searchQuery,
    sortBy,
    category,
    brand,
  };

  const { data, isLoading, error, refetch } = useQuery<PaginatedCatalogResponse, Error>(
    ['catalog', params],
    () => fetcher<PaginatedCatalogResponse>(`${CATALOG_ENDPOINT}?${new URLSearchParams(params as any)}`),
  );

  const products = data?.products || [];
  const totalItems = data?.totalItems || 0;
  const totalPages = data?.totalPages || 0;
  const currentPage = data?.currentPage || 1;
  const currentBrandColor = brandColors[brand] || 'blue-500';

  return {
    products,
    totalItems,
    totalPages,
    currentPage,
    pageSize,
    isLoading,
    error,
    refetch,
    brand,
    brandColor: currentBrandColor,
  };
};