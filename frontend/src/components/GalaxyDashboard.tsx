import React from 'react';
import React, { useState } from "react";
import { Product } from "@/types/Product";
import { useGalaxyData } from "@/hooks/useGalaxyData";

/**
 * ProductCard: Individual product card component
 */
interface ProductCardProps {
  product: Product;
  onClick?: () => void;
}

const ProductCard: React.FC<ProductCardProps> = ({ product, onClick }) => {
  const riskColor =
    product.risk_score > 50
      ? "text-red-500"
      : product.risk_score > 20
        ? "text-yellow-500"
        : "text-green-500";

  return (
    <div
      className="bg-slate-800 rounded-lg overflow-hidden hover:shadow-lg hover:shadow-blue-500/50 transition-all cursor-pointer transform hover:scale-105"
      onClick={onClick}
    >
      {/* Image */}
      <div className="w-full h-48 bg-slate-700 overflow-hidden">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).src =
              "https://via.placeholder.com/300x200?text=No+Image";
          }}
        />
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Name */}
        <h3 className="font-bold text-white text-lg truncate">
          {product.name}
        </h3>

        {/* Category */}
        <p className="text-slate-400 text-sm mb-3">{product.category}</p>

        {/* Price & Risk */}
        <div className="flex justify-between items-center mb-3">
          <span className="text-blue-500 font-semibold text-lg">
            ${product.price.toFixed(2)}
          </span>
          <span className={`text-xs font-mono ${riskColor}`}>
            Risk: {product.risk_score}
          </span>
        </div>

        {/* Verified Badge */}
        {product.verified && (
          <div className="inline-block bg-green-900 text-green-300 text-xs px-2 py-1 rounded">
            ✓ Verified
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * GalaxyDashboard: Main component for product grid display
 */
const GalaxyDashboard: React.FC = () => {
  const {
    products: allProducts,
    loading,
    error,
    filteredProducts,
  } = useGalaxyData();
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");

  // Get unique categories
  const categories = ["All", ...new Set(allProducts.map((p) => p.category))];

  // Apply both search and category filters
  let displayProducts = allProducts;

  if (searchQuery.trim()) {
    displayProducts = displayProducts.filter(
      (p) =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.category.toLowerCase().includes(searchQuery.toLowerCase()),
    );
  }

  if (categoryFilter !== "All") {
    displayProducts = displayProducts.filter(
      (p) => p.category === categoryFilter,
    );
  }

  // Handlers
  const handleProductClick = (product: Product) => {    // TODO: Navigate to detail view or open modal
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  const handleCategoryChange = (category: string) => {
    setCategoryFilter(category);
  };

  const handleReset = () => {
    setSearchQuery("");
    setCategoryFilter("All");
  };

  // Render
  return (
    <div className="min-h-screen bg-slate-900 p-6 sm:p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl sm:text-5xl font-bold text-white mb-2">
          Galaxy Dashboard
        </h1>
        <p className="text-slate-400 text-sm sm:text-base">
          {displayProducts.length} product
          {displayProducts.length !== 1 ? "s" : ""} available
        </p>
      </div>

      {/* Filters */}
      <div className="mb-8 space-y-4">
        {/* Search Input */}
        <div>
          <input
            type="text"
            placeholder="Search by name or category..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full px-4 py-3 bg-slate-800 text-white border border-slate-700 rounded-lg focus:border-blue-500 focus:outline-none transition"
          />
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => handleCategoryChange(cat)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                categoryFilter === cat
                  ? "bg-blue-500 text-white"
                  : "bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Reset Button */}
        {(searchQuery || categoryFilter !== "All") && (
          <button
            onClick={handleReset}
            className="px-4 py-2 bg-slate-700 text-slate-300 rounded-lg hover:bg-slate-600 transition text-sm"
          >
            Reset Filters
          </button>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex justify-center items-center min-h-96">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
            <p className="text-slate-400">Loading products...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 text-red-300 p-4 rounded-lg mb-6">
          <p className="font-semibold">Error Loading Products</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && displayProducts.length === 0 && (
        <div className="flex flex-col justify-center items-center min-h-96">
          <p className="text-slate-400 text-lg mb-4">No products found</p>
          <button
            onClick={handleReset}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Product Grid */}
      {!loading && !error && displayProducts.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-max">
          {displayProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onClick={() => handleProductClick(product)}
            />
          ))}
        </div>
      )}

      {/* Footer */}
      <div className="mt-12 pt-8 border-t border-slate-700 text-center">
        <p className="text-slate-500 text-sm">
          Powered by Conductor v5.2.4 | Last updated:{" "}
          {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default GalaxyDashboard;
