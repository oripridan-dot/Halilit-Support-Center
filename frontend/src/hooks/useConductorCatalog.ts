import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ImageWithFallback } from '../components/ImageWithFallback';
import { ResearchAnimation } from '../components/ResearchAnimation';
import { Skeleton } from '../components/Skeleton';
import { MagnifyingGlass } from 'lucide-react';
import { motion } from 'framer-motion';

const defaultPageSize = 25;

interface UseConductorCatalogProps {
    page?: number;
    pageSize?: number;
    searchQuery?: string;
    sortBy?: string;
    category?: string;
    brand?: string;
}

export const useConductorCatalog = (props: UseConductorCatalogProps = {}) => {
    const { page = 1, pageSize = defaultPageSize, searchQuery = '', sortBy = '', category = '', brand = '' } = props;
    const [isError, setIsError] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');

    const params: CatalogRequestParams = {
        page,
        pageSize,
        searchQuery,
        sortBy,
        category,
        brand,
    };

    const { data, isLoading, isError: queryIsError, error, refetch } = useQuery<PaginatedCatalogResponse, Error>(
        ['catalog', params],
        async () => {
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
            return response.json();
        },
        {
            keepPreviousData: true,
        }
    );

    useEffect(() => {
        if (queryIsError && error) {
            setIsError(true);
            setErrorMessage(error.message);
        } else {
            setIsError(false);
            setErrorMessage('');
        }
    }, [queryIsError, error]);

    const products = data?.products || [];
    const totalItems = data?.totalItems || 0;
    const totalPages = data?.totalPages || 0;
    const currentPage = data?.currentPage || 1;
    const pageSize = data?.pageSize || defaultPageSize;


    return {
        products,
        totalItems,
        totalPages,
        currentPage,
        pageSize,
        isLoading,
        isError,
        errorMessage,
        refetch,
    };
};

export const CatalogLoadingIndicator = () => {
  return (
    <div className="absolute top-0 left-0 w-full h-full bg-slate-900 z-10 flex items-center justify-center">
      <motion.div
        animate={{ scale: [0.8, 1.2] }}
        transition={{ duration: 1.5, ease: 'easeInOut', repeat: Infinity, repeatType: 'reverse' }}
      >
        <MagnifyingGlass className="text-blue-500 h-8 w-8" />
      </motion.div>
    </div>
  );
};


export const CatalogSkeleton = () => {
    return (
        <div className="space-y-4">
            {[...Array(5)].map((_, index) => (
                <div key={index} className="flex items-center space-x-4">
                    <Skeleton className="h-24 w-24 rounded-md" />
                    <div className="space-y-2 w-full">
                        <Skeleton className="h-4 w-3/4 rounded-md" />
                        <Skeleton className="h-4 w-1/2 rounded-md" />
                    </div>
                </div>
            ))}
        </div>
    );
};