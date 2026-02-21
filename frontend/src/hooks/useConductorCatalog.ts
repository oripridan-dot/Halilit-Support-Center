import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MagnifyingGlass } from 'lucide-react';
import { motion } from 'framer-motion';

interface Props {
    searchQuery: string;
    category?: string;
    brand?: string;
}

const useConductorCatalog = ({ searchQuery, category, brand }: Props) => {
    const [page, setPage] = useState<number>(1);
    const [pageSize, setPageSize] = useState<number>(25);
    const [sortBy, setSortBy] = useState<string>('');

    const params: CatalogRequestParams = useMemo(() => ({
        page,
        pageSize,
        searchQuery,
        sortBy,
        category,
        brand,
    }), [page, pageSize, searchQuery, sortBy, category, brand]);

    const { data, isLoading, error, refetch } = useQuery<PaginatedCatalogResponse, Error>({
        queryKey: ['conductorCatalog', params],
        queryFn: async () => {
            const searchParams = new URLSearchParams();
            if (params.page) searchParams.append('page', params.page.toString());
            if (params.pageSize) searchParams.append('pageSize', params.pageSize.toString());
            if (params.searchQuery) searchParams.append('searchQuery', params.searchQuery);
            if (params.sortBy) searchParams.append('sortBy', params.sortBy);
            if (params.category) searchParams.append('category', params.category);
            if (params.brand) searchParams.append('brand', params.brand);

            const url = `${CATALOG_ENDPOINT}?${searchParams.toString()}`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json() as Promise<PaginatedCatalogResponse>;
        },
        onError: (err) => {
            console.error("Error fetching catalog:", err);
        },
    });

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
        refetch,
        setPage,
        setPageSize,
        setSortBy,
    };
};

export default useConductorCatalog;