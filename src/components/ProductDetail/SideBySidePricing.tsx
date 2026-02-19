import React, { useState, useEffect } from 'react';
import { PricingData, SideBySidePricingProps } from './types'; // Assuming types are in a types.ts file

const SideBySidePricing: React.FC<SideBySidePricingProps> = ({ productId }) => {
  const [pricingData, setPricingData] = useState<PricingData[] | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPricingData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/products/${productId}/pricing`);
        if (!response.ok) {
          throw new Error(`Failed to fetch pricing data: ${response.status}`);
        }
        const data: PricingData[] = await response.json();
        setPricingData(data);
      } catch (error: any) {
        setError(error.message || 'Failed to load pricing data. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPricingData();
  }, [productId]);

  if (isLoading) {
    return <div className="text-center py-4">Loading pricing information...</div>;
  }

  if (error) {
    return <div className="text-center py-4 text-red-500">{error}</div>;
  }

  if (!pricingData || pricingData.length === 0) {
    return <div className="text-center py-4">No pricing information available for this product.</div>;
  }

  const vendorColors = ['bg-slate-900', 'bg-blue-500']; // Add more if you expect more vendors
  const textColor = 'text-white'; // or appropriate contrast color

  return (
    <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
      {pricingData.map((vendor, index) => (
        <div key={vendor.vendor_id} className={`w-full md:w-1/2 rounded-lg overflow-hidden shadow-md ${vendorColors[index % vendorColors.length]}`}>
          <div className={`p-4 ${textColor}`}>
            <h3 className="text-lg font-semibold mb-2">{vendor.vendor_name}</h3>
            <div className="text-2xl font-bold mb-2">
              {vendor.currency} {vendor.price.toFixed(2)}
            </div>
            {vendor.shipping_cost === null || vendor.shipping_cost === undefined ? (
              <p className="mb-2">Free Shipping</p>
            ) : (
              <p className="mb-2">Shipping: {vendor.currency} {vendor.shipping_cost.toFixed(2)}</p>
            )}
            {vendor.estimated_delivery === null || vendor.estimated_delivery === undefined ? (
              <p className="mb-2">Not available</p>
            ) : (
              <p className="mb-2">Estimated Delivery: {vendor.estimated_delivery}</p>
            )}
            <a href={vendor.product_url} target="_blank" rel="noopener noreferrer" className="inline-block px-4 py-2 rounded-md bg-white text-blue-500 hover:bg-gray-100">
              View Product
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SideBySidePricing;