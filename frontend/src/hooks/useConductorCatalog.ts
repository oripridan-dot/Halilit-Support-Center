import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import {
  CatalogRequestParams,
  PaginatedCatalogResponse,
  ConductorProduct,
  CATALOG_ENDPOINT,
import { ImageWithFallback } from '../components/ImageWithFallback';
import { ResearchAnimation } from '../components/ResearchAnimation';
import { useDebounce } from './useDebounce';

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
}: UseConductorCatalogProps = {}) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  const params: CatalogRequestParams = {
    page,
    pageSize,
    searchQuery: debouncedSearchQuery,
    sortBy,
    category,
    brand,
  };

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useQuery<PaginatedCatalogResponse, Error>(
    ['catalog', params],
    async () => {
      const url = new URL(CATALOG_ENDPOINT, window.location.origin);
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          url.searchParams.append(key, String(value));
        }
      });
      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json() as Promise<PaginatedCatalogResponse>;
    },
  );

  const handlePageChange = (newPage: number) => {
    setSearchParams(prevParams => {
      const newParams = new URLSearchParams(prevParams);
      newParams.set('page', String(newPage));
      return newParams;
    });
  };

  return {
    products: data?.products || [],
    totalItems: data?.totalItems || 0,
    totalPages: data?.totalPages || 0,
    currentPage: data?.currentPage || 1,
    pageSize: data?.pageSize || 25,
    isLoading,
    error,
    refetch,
    handlePageChange,
  };
};