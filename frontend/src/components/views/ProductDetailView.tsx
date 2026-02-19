import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useNavigationStore } from '../../store/navigationStore';
import { Accessory } from '../../types';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Image from 'next/image';

interface AccessoryProduct {
    id: number;
    name: string;
    imageUrl: string;
    price: number | null;
    url: string; // URL to the product detail page
}

const PlaceholderImage = '/placeholder.png';

const useProductRelationships = (productId: string | undefined) => {
    const [accessories, setAccessories] = useState<AccessoryProduct[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchAccessories = async () => {
            if (!productId) return;
            setLoading(true);
            setError(null);
            try {
                const response = await fetch(`/api/v1/products/${productId}/accessories`);
                if (response.ok) {
                    const data = await response.json();
                    setAccessories(data);
                } else if (response.status === 204) {
                    setAccessories([]);
                } else {
                    const errorData = await response.json();
                    setError(errorData.detail || 'Failed to load accessories');
                }
            } catch (err: any) {
                setError(err.message || 'Failed to load accessories');
            } finally {
                setLoading(false);
            }
        };

        fetchAccessories();
    }, [productId]);

    const refetch = () => {
        if (productId) {
            fetchAccessories();
        }
    };

    return { accessories, loading, error, refetch };
};

const AccessoryTile: React.FC<{ accessory: AccessoryProduct }> = ({ accessory }) => {
    const navigation = useNavigationStore();

    const handleTileClick = () => {
        navigation.goToProduct(accessory.id.toString());
    };

    return (
        <div
            className="w-48 rounded-lg shadow-md bg-slate-800 hover:bg-slate-700 transition-colors duration-200 cursor-pointer"
            onClick={handleTileClick}
            tabIndex={0}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleTileClick();
                }
            }}
        >
            <Image
                src={accessory.imageUrl || PlaceholderImage}
                alt={accessory.name}
                width={192}
                height={108}
                className="rounded-t-lg object-cover"
                onError={(e) => {
                    (e.target as HTMLImageElement).src = PlaceholderImage;
                }}
            />
            <div className="p-2">
                <p className="text-white text-sm font-medium">{accessory.name}</p>
                <p className="text-gray-300 text-sm">
                    {accessory.price === null ? 'Call for Price' : `$${accessory.price?.toFixed(2)}`}
                </p>
            </div>
        </div>
    );
};

const AccessoryRecommendations: React.FC = () => {
    const { productId } = useParams<{ productId: string }>();
    const { accessories, loading, error, refetch } = useProductRelationships(productId);

    if (!productId) {
        return null;
    }

    return (
        <div className="py-4">
            <h2 className="text-xl text-white font-semibold mb-2">Recommended Accessories</h2>

            {loading && (
                <div className="flex space-x-4 overflow-x-auto py-2">
                    {[...Array(3)].map((_, index) => (
                        <div key={index} className="w-48 h-64 rounded-lg shadow-md bg-slate-700 animate-pulse"></div>
                    ))}
                </div>
            )}

            {error && (
                <div className="bg-red-900 p-4 rounded flex items-center gap-2">
                    <AlertTriangle size={20} className="text-red-500" />
                    <span className="text-red-500">Error loading accessories: {error}</span>
                    <button onClick={refetch} className="text-blue-500 hover:text-blue-300 ml-2">
                        <RefreshCw size={20} />
                    </button>
                </div>
            )}

            {!loading && !error && accessories.length === 0 && (
                <div className="bg-amber-900 p-4 rounded flex items-center gap-2">
                    <AlertTriangle size={20} className="text-amber-500" />
                    <span className="text-amber-300">No accessories found. Please check the product graph and add compatible accessories.</span>
                </div>
            )}

            {!loading && !error && accessories.length > 0 && (
                <div className="overflow-x-auto py-2">
                    <div className="flex space-x-4 pb-2">
                        {accessories.map((accessory) => (
                            <AccessoryTile key={accessory.id} accessory={accessory} />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default AccessoryRecommendations;