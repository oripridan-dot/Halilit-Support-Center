/**
 * Product Type Definitions
 * Strict interfaces for type-safe product handling in Galaxy Dashboard
 */

export interface Product {
    id: string;
    name: string;
    category: string;
    price: number;
    currency: string;
    image_url: string;
    risk_score: number; // 0-100
    verified: boolean;
    source_url: string;
}

export interface ProductCardProps {
    product: Product;
    onClick?: () => void;
}

export interface GalaxyDashboardProps {
    onProductClick?: (product: Product) => void;
}

export interface ExportResponse {
    products: Product[];
    total_count: number;
    last_updated: string;
}
