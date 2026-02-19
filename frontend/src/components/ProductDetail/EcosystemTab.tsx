import React, { useState, useEffect } from 'react';
import { useNavigationStore } from '../../store/navigationStore';

interface EcosystemData {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

interface RelatedProduct {
  product_id: string;
  name: string;
  description: string;
  image_url: string;
  product_url: string;
}

interface Integration {
  integration_id: string;
  name: string;
  description: string;
  logo_url: string;
  integration_url: string;
}

interface Props {
  productId: string;
}

const EcosystemTab: React.FC<Props> = ({ productId }) => {
  const [data, setData] = useState<EcosystemData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigation = useNavigationStore();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/products/${productId}/ecosystem`);
        if (!response.ok) {
          const errorData = await response.json();
          setError(errorData.detail || 'Failed to fetch ecosystem data');
          throw new Error('Failed to fetch ecosystem data');
        }
        const jsonData: EcosystemData = await response.json();
        setData(jsonData);
      } catch (err) {
        // Error is already set in the if (!response.ok) block
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [productId]);

  const handleProductClick = (productId: string) => {
    navigation.goToProduct(productId);
  };

  return (
    <div className="p-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>{' '}
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center">
          <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 6.627 5.373 12 12 12v-7.291z"></path>
          </svg>
        </div>
      )}

      {!loading && !error && (
        <>
          <section className="mb-4">
            <h2 className="text-lg font-semibold mb-2">Related Products</h2>
            {data?.related_products && data.related_products.length > 0 ? (
              <div className="flex space-x-4 overflow-x-auto">
                {data.related_products.map((product) => (
                  <div key={product.product_id} className="w-64 flex-shrink-0 border rounded-lg shadow-md hover:shadow-lg transition duration-200 ease-in-out">
                    <button onClick={() => handleProductClick(product.product_id)} className="w-full h-full">
                      {product.image_url && (
                        <img src={product.image_url} alt={product.name} className="w-full h-40 object-cover rounded-t-lg" />
                      )}
                      <div className="p-4">
                        <h3 className="text-md font-medium mb-1">{product.name}</h3>
                        <p className="text-gray-700 dark:text-gray-300 text-sm">{product.description}</p>
                      </div>
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative" role="alert">
                <span className="block sm:inline">No related products found</span>
              </div>
            )}
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2">Integrations</h2>
            {data?.integrations && data.integrations.length > 0 ? (
              <div className="flex space-x-4 overflow-x-auto">
                {data.integrations.map((integration) => (
                  <div key={integration.integration_id} className="w-64 flex-shrink-0 border rounded-lg shadow-md hover:shadow-lg transition duration-200 ease-in-out">
                    <a href={integration.integration_url} target="_blank" rel="noopener noreferrer" className="w-full h-full">
                      {integration.logo_url && (
                        <img src={integration.logo_url} alt={integration.name} className="w-full h-40 object-cover rounded-t-lg" />
                      )}
                      <div className="p-4">
                        <h3 className="text-md font-medium mb-1">{integration.name}</h3>
                        <p className="text-gray-700 dark:text-gray-300 text-sm">{integration.description}</p>
                      </div>
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative" role="alert">
                <span className="block sm:inline">No integrations found</span>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};

export default EcosystemTab;