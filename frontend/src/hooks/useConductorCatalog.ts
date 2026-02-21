import React, { useState, useMemo } from 'react';
import { Input } from '@/components/ui/input';
import { useConductorCatalog } from '@/hooks/useConductorCatalog';
import { Search } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

const GlobalSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState(searchParams.get('searchQuery') || '');

  const { refetch } = useConductorCatalog({
    searchQuery: searchTerm,
    page: parseInt(searchParams.get('page') || '1', 10),
    pageSize: parseInt(searchParams.get('pageSize') || '25', 10),
    sortBy: searchParams.get('sortBy') || undefined,
    category: searchParams.get('category') || undefined,
    brand: searchParams.get('brand') || undefined,
  });

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleSearchSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSearchParams(prevParams => {
      prevParams.set('searchQuery', searchTerm);
      prevParams.set('page', '1');
      return prevParams;
    });
    await refetch();
  };

  return (
    <form onSubmit={handleSearchSubmit} className="relative w-full">
      <div className="absolute inset-y-0 left-0 flex items-center pl-3">
        <Search className="h-4 w-4 text-zinc-400 dark:text-zinc-500" />
      </div>
      <Input
        type="search"
        placeholder="Search products..."
        value={searchTerm}
        onChange={handleSearchChange}
        className="w-full rounded-md border border-zinc-200 bg-zinc-50 pl-10 pr-4 text-sm text-zinc-900 placeholder:text-zinc-400 focus:border-blue-500 focus:ring-blue-500 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-100 dark:placeholder:text-zinc-500"
      />
    </form>
  );
};

export default GlobalSearch;