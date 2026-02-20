import React, { useState, useEffect } from "react";
import { Loader2, AlertTriangle } from "lucide-react";

const VENDOR_STYLES = [
  "bg-zinc-800",
  "bg-blue-900",
  "bg-green-900",
  "bg-purple-900",
  "bg-red-900",
];

const SideBySidePricing: React.FC<SideBySidePricingProps> = ({ productId }) => {
  const [pricingData, setPricingData] = useState<PricingData[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPricing = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/products/${productId}/pricing`);
        if (!response.ok) {
          throw new Error("Failed to fetch pricing data");
        }
        const data = await response.json();
        setPricingData(data);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPricing();
  }, [productId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-20 bg-zinc-900 rounded-xl">
        <Loader2 className="animate-spin h-6 w-6 text-zinc-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-zinc-900 rounded-xl p-4 text-red-400">
        <div className="flex items-center gap-2">
          <AlertTriangle size={16} />
          {error}
        </div>
      </div>
    );
  }

  if (!pricingData || pricingData.length === 0) {
    return (
      <div className="bg-zinc-900 rounded-xl p-4 text-zinc-400">
        No pricing information available for this product.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {pricingData.map((vendor, index) => (
        <div
          key={vendor.vendor_id}
          className={`rounded-xl overflow-hidden ${VENDOR_STYLES[index % VENDOR_STYLES.length]}`}
        >
          <div className="p-4">
            <div className="text-white font-bold text-lg mb-2">{vendor.vendor_name}</div>
            <div className="text-zinc-300 text-sm mb-2">
              {vendor.currency} {vendor.price.toFixed(2)}
            </div>
            <div className="text-zinc-400 text-xs mb-2">
              {vendor.shipping_cost === null || vendor.shipping_cost === undefined
                ? "Free Shipping"
                : `Shipping: ${vendor.currency} ${vendor.shipping_cost.toFixed(2)}`}
            </div>
            <div className="text-zinc-400 text-xs mb-2">
              {vendor.estimated_delivery === null || vendor.estimated_delivery === undefined
                ? "Not available"
                : `Delivery: ${vendor.estimated_delivery}`}
            </div>
            <a
              href={vendor.product_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block px-4 py-2 mt-2 text-sm font-medium text-blue-400 hover:underline"
            >
              View Product
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

export default SideBySidePricing;