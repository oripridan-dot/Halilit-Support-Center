import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetcher } from '../utils/fetcher';
import { ImageWithFallback } from '../../components/ImageWithFallback';

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
    const params: CatalogRequestParams = {
        page,
        pageSize,
        searchQuery,
        sortBy,
        category,
        brand,
    };

    const { data, isLoading, isError, error, refetch } = useQuery<PaginatedCatalogResponse, Error>(
        ['conductorCatalog', params],
        () => fetcher<PaginatedCatalogResponse>(CATALOG_ENDPOINT, { params }),
        {
            keepPreviousData: true,
        }
    );

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
        itemsPerPage,
        isLoading,
        isError,
        error,
        refetch,
    };
};

export { useConductorCatalog };