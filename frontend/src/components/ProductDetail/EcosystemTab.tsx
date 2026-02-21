import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";
import ImageWithFallback from "../ImageWithFallback";

/**
 * Represents the data structure for the ecosystem tab, including related products and integrations.
 */
interface EcosystemData {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

/**
 * Represents a related product in the ecosystem.
 */
interface RelatedProduct {
  product_id: string;
  name: string;
  description: string;
  image_url: string;
  product_url: string;
  _pinned?: boolean; // Added for optimistic updates
}

/**
 * Represents an integration in the ecosystem.
 */
interface Integration {
  integration_id: string;
  name: string;
  description: string;
  logo_url: string;
  integration_url: string;
}

/**
 * Props for the EcosystemTab component.
 */
interface EcosystemTabProps {
  productId: string;
}

/**
 * Fetches ecosystem data for a given product ID.
 * @param productId The ID of the product to fetch ecosystem data for.
 * @returns A promise that resolves to the ecosystem data.
 */
async function fetchEcosystem(productId: string): Promise<EcosystemData> {
  const res = await fetch(`/api/products/${productId}/ecosystem`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `Ecosystem fetch failed (${res.status})`);
  }
  return res.json() as Promise<EcosystemData>;
}

/**
 * Displays related products and integrations for a given product.
 */
const EcosystemTab: React.FC<EcosystemTabProps> = ({ productId }) => {
  const navigation = useNavigationStore();
  const queryClient = useQueryClient();

  // ── Primary query ──────────────────────────────────────────────────────
  const { data: ecosystemData, isLoading, error } = useQuery<EcosystemData, Error>({
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
      await queryClient.cancelQueries({ queryKey: ["ecosystem", productId] });
      const previousEcosystemData = queryClient.getQueryData<EcosystemData>(["ecosystem", productId]);

      // Optimistically mark the product as pinned in cached data
      if (previousEcosystemData) {
        queryClient.setQueryData<EcosystemData>(["ecosystem", productId], {
          ...previousEcosystemData,
          related_products: previousEcosystemData.related_products.map((product) =>
            product.product_id === relatedId
              ? ({ ...product, _pinned: true })
              : product,
          ),
        });
      }
      return { previousEcosystemData };
    },
    onError: (_err, _relatedId, context) => {
      // Roll back on failure
      if (context?.previousEcosystemData) {
        queryClient.setQueryData(["ecosystem", productId], context.previousEcosystemData);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["ecosystem", productId] });
    },
  });

  /**
   * Navigates to the product details page for a given product ID.
   * @param productId The ID of the product to navigate to.
   */
  const handleProductClick = (productId: string) => navigation.goToProduct(productId);

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
        {ecosystemData?.related_products && ecosystemData.related_products.length > 0 ? (
          <div className="flex space-x-4 overflow-x-auto">
            {ecosystemData.related_products.map((product) => (
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
        {ecosystemData?.integrations && ecosystemData.integrations.length > 0 ? (
          <div className="flex space-x-4 overflow-x-auto">
            {ecosystemData.integrations.map((integration) => (
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