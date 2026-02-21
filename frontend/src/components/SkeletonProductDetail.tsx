import React from 'react';

const SkeletonProductDetail: React.FC = () => {
  return (
    <div className="bg-slate-900 p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Hero Image Placeholder */}
      <div className="md:col-span-1 rounded-lg overflow-hidden">
        <div className="aspect-w-16 aspect-h-9">
          <div className="animate-shimmer w-full h-full bg-zinc-700" />
        </div>
      </div>

      <div className="md:col-span-1">
        {/* Product Title Placeholder */}
        <div className="animate-shimmer h-5 w-3/4 bg-zinc-700 rounded-md mb-2" />

        {/* Brand Placeholder */}
        <div className="animate-shimmer h-4 w-1/2 bg-zinc-700 rounded-md mb-4" />

        {/* Price Placeholder */}
        <div className="animate-shimmer h-6 w-1/3 bg-zinc-700 rounded-md mb-4" />

        {/* Description Placeholder */}
        <div className="space-y-2">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="animate-shimmer h-4 w-full bg-zinc-700 rounded-md" />
          ))}
        </div>
      </div>

      {/* Related Products Section */}
      <div className="md:col-span-2">
        <h3 className="text-zinc-400 font-medium mb-2">Related Products</h3>
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="w-1/3 shrink-0 rounded-lg overflow-hidden shadow-md">
              <div className="aspect-w-4 aspect-h-3">
                <div className="animate-shimmer w-full h-full bg-zinc-700" />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Integrations Section */}
      <div className="md:col-span-2">
        <h3 className="text-zinc-400 font-medium mb-2">Integrations</h3>
        <div className="flex space-x-4 overflow-x-auto pb-4">
          {[...Array(2)].map((_, index) => (
            <div key={index} className="w-1/2 shrink-0 rounded-lg overflow-hidden shadow-md">
              <div className="aspect-w-4 aspect-h-3">
                <div className="animate-shimmer w-full h-full bg-zinc-700" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SkeletonProductDetail;