import React, { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { EcosystemTab } from '../ProductDetail/EcosystemTab';
import { useNavigationStore } from '../../store/navigationStore';
import { AlertTriangle } from 'lucide-react';

const ProductDetailView: React.FC = () => {
    const { productId } = useParams<{ productId: string }>();
    const navigation = useNavigationStore();
    const [activeTab, setActiveTab] = useState('overview');

    const handleTabClick = (tab: string) => {
        setActiveTab(tab);
    };

    if (!productId) {
        return (
            <div className="bg-zinc-950 min-h-screen p-4 flex flex-col items-center justify-center">
                <div className="bg-red-800 text-white p-4 rounded flex items-center gap-2">
                    <AlertTriangle size={20} />
                    <span>Product ID is missing.</span>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-zinc-950 min-h-screen p-4">
            <div className="flex items-center space-x-4 mb-4">
                <button
                    className={`px-4 py-2 rounded-md ${activeTab === 'overview' ? 'bg-blue-500 text-white' : 'bg-zinc-800 text-white hover:bg-zinc-700'
                        }`}
                    onClick={() => handleTabClick('overview')}
                >
                    Overview
                </button>
                <button
                    className={`px-4 py-2 rounded-md ${activeTab === 'ecosystem' ? 'bg-blue-500 text-white' : 'bg-zinc-800 text-white hover:bg-zinc-700'
                        }`}
                    onClick={() => handleTabClick('ecosystem')}
                >
                    Ecosystem
                </button>
            </div>

            {activeTab === 'overview' && (
                <div className="text-white">
                    {/* Placeholder for product details */}
                    <p>Product Details Placeholder</p>
                </div>
            )}

            {activeTab === 'ecosystem' && (
                <EcosystemTab productId={productId} />
            )}
        </div>
    );
};

export default ProductDetailView;