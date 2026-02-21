import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";
import ImageWithFallback from "../ImageWithFallback";

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

async function fetchEcosystem(productId: string): Promise<EcosystemData> {
  const res = await fetch(`/api/products/${productId}/ecosystem`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `Ecosystem fetch failed (${res.status})`);
  }
  return res.json() as Promise<EcosystemData>;
}

const EcosystemTab: React.FC<Props> = ({ productId }) => {
  const navigation = useNavigationStore();
  const qc = useQueryClient();

  // ── Primary query ──────────────────────────────────────────────────────
  const { data, isLoading, error } = useQuery<EcosystemData, Error>({
    queryKey: ["ecosystem", productId],
    queryFn: () => fetchEcosystem(productId),
    staleTime: 60_000,
    retry: 1,
  });

  // ── Optimistic accessory pin / unpin mutation ──────────────────────────
  // When a product is "pinned" as an accessory the UI reflects the change
  // immediately (optimistic update) and the server is updated in background.
  const { mutate: pinAccessory } = useMutation({
    mutationFn: async (relatedId: string) => {
      const res = await fetch(`/api/products/${productId}/pin-accessory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ related_id: relatedId }),
      });
      if (!res.ok) throw new Error("Pin failed");
    },
    onMutate: async (relatedId: string) => {
      // Cancel any outgoing re-fetches to avoid overwriting our optimistic update
      await qc.cancelQueries({ queryKey: ["ecosystem", productId] });
      const prev = qc.getQueryData<EcosystemData>(["ecosystem", productId]);

      // Optimistically mark the product as pinned in cached data
      if (prev) {
        qc.setQueryData<EcosystemData>(["ecosystem", productId], {
          ...prev,
          related_products: prev.related_products.map((p) =>
            p.product_id === relatedId
              ? ({ ...p, _pinned: true } as RelatedProduct & {
                  _pinned?: boolean;
                })
              : p,
          ),
        });
      }
      return { prev };
    },
    onError: (_err, _relatedId, ctx) => {
      // Roll back on failure
      if (ctx?.prev) {
        qc.setQueryData(["ecosystem", productId], ctx.prev);
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ["ecosystem", productId] });
    },
  });

  const handleProductClick = (id: string) => navigation.goToProduct(id);

  // ── Render ─────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="p-4">
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded"
          role="alert"
        >
          <strong className="font-bold">Error!</strong>{" "}
          <span className="block sm:inline">{error.message}</span>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-4 flex items-center justify-center">
        <svg
          className="animate-spin h-5 w-5 text-blue-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 6.627 5.373 12 12 12v-7.291z"
          />
        </svg>
      </div>
    );
  }

  return (
    <div className="p-4">
      <section className="mb-4">
        <h2 className="text-lg font-semibold mb-2">Related Products</h2>
        {data?.related_products && data.related_products.length > 0 ? (
          <div className="flex space-x-4 overflow-x-auto">
            {data.related_products.map((product) => (
              <div
                key={product.product_id}
                className="w-64 flex-shrink-0 border border-zinc-700 rounded-lg shadow-md hover:shadow-lg transition duration-200"
              >
                <ImageWithFallback
                  imageUrl={product.image_url}
                  altText={product.name}
                  className="w-full h-40 rounded-t-lg object-contain bg-zinc-900"
                />
                <div className="p-4">
                  <h3 className="text-md font-semibold mb-1">{product.name}</h3>
                  <p className="text-sm text-zinc-400">{product.description}</p>
                  <div className="mt-2 flex gap-2">
                    <button
                      onClick={() => handleProductClick(product.product_id)}
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-1.5 px-3 rounded text-sm"
                    >
                      View
                    </button>
                    <button
                      onClick={() => pinAccessory(product.product_id)}
                      className="bg-zinc-700 hover:bg-zinc-600 text-white font-bold py-1.5 px-3 rounded text-sm"
                      title="Pin as accessory"
                    >
                      ＋
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-zinc-500 text-sm">No related products found.</p>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-2">Integrations</h2>
        {data?.integrations && data.integrations.length > 0 ? (
          <div className="flex space-x-4 overflow-x-auto">
            {data.integrations.map((integration) => (
              <div
                key={integration.integration_id}
                className="w-64 flex-shrink-0 border border-zinc-700 rounded-lg shadow-md hover:shadow-lg transition duration-200"
              >
                <ImageWithFallback
                  imageUrl={integration.logo_url}
                  altText={integration.name}
                  className="w-full h-40 rounded-t-lg object-contain bg-zinc-900"
                />
                <div className="p-4">
                  <h3 className="text-md font-semibold mb-1">
                    {integration.name}
                  </h3>
                  <p className="text-sm text-zinc-400">
                    {integration.description}
                  </p>
                  <a
                    href={integration.integration_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-1.5 px-4 rounded text-sm"
                  >
                    View Integration
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-zinc-500 text-sm">No integrations found.</p>
        )}
      </section>
    </div>
  );
};

export default EcosystemTab;

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
          setError(errorData.detail || "Failed to fetch ecosystem data");
          throw new Error("Failed to fetch ecosystem data");
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
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative"
          role="alert"
        >
          <strong className="font-bold">Error!</strong>{" "}
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center">
          <svg
            className="animate-spin h-5 w-5 text-blue-500"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 6.627 5.373 12 12 12v-7.291z"
            ></path>
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
                  <div
                    key={product.product_id}
                    className="w-64 flex-shrink-0 border rounded-lg shadow-md hover:shadow-lg transition duration-200 ease-in-out"
                  >
                    <ImageWithFallback
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-40 rounded-t-lg"
                    />
                    <div className="p-4">
                      <h3 className="text-md font-semibold mb-1">
                        {product.name}
                      </h3>
                      <p className="text-sm text-gray-700">
                        {product.description}
                      </p>
                      <button
                        onClick={() => handleProductClick(product.product_id)}
                        className="mt-2 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No related products found</p>
            )}
          </section>

          <section>
            <h2 className="text-lg font-semibold mb-2">Integrations</h2>
            {data?.integrations && data.integrations.length > 0 ? (
              <div className="flex space-x-4 overflow-x-auto">
                {data.integrations.map((integration) => (
                  <div
                    key={integration.integration_id}
                    className="w-64 flex-shrink-0 border rounded-lg shadow-md hover:shadow-lg transition duration-200 ease-in-out"
                  >
                    <ImageWithFallback
                      src={integration.logo_url}
                      alt={integration.name}
                      className="w-full h-40 rounded-t-lg"
                    />
                    <div className="p-4">
                      <h3 className="text-md font-semibold mb-1">
                        {integration.name}
                      </h3>
                      <p className="text-sm text-gray-700">
                        {integration.description}
                      </p>
                      <a
                        href={integration.integration_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="mt-2 inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                      >
                        View Integration
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No integrations found</p>
            )}
          </section>
        </>
      )}
    </div>
  );
};

export default EcosystemTab;
