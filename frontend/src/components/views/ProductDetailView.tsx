import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import type { ConductorProduct } from '../../hooks/useConductorCatalog';
import { useNavigationStore } from '../../store/navigationStore';
import { ExternalLink, Check, ClipboardCopy, AlertTriangle } from 'lucide-react';
import { ImageWithFallback } from '../ImageWithFallback';
import { ProductImageCarousel } from '../ProductImageCarousel';
import { EcosystemTab } from '../EcosystemTab';
import JITBadge from '../ProductDetail/JITBadge';
import SourcingBadge from '../ProductDetail/SourcingBadge';
import { useJITIntelligence } from '../../hooks/useJITIntelligence';

const ProductDetailView: React.FC = () => {
  const { products } = useConductorCatalog();
  const { activeProductId } = useNavigationStore();
  const navigate = useNavigate();
  const { productId } = useParams<{ productId: string }>();
  const [copied, setCopied] = useState(false);
  const { jitState, refetch } = useJITIntelligence(productId || '');
  const [activeTab, setActiveTab] = useState('overview');

  const product = useMemo<ConductorProduct | null>(
    () => products.find(p => p.id === (productId || activeProductId)) ?? null,
    [products, productId, activeProductId]
  );

  useEffect(() => {
    if (copied) {
      const timeout = setTimeout(() => setCopied(false), 2000);
      return () => clearTimeout(timeout);
    }
  }, [copied]);

  const handleCopySKU = async () => {
    if (!product?.id) return;
    try {
      await navigator.clipboard.writeText(product.id);
      setCopied(true);
    } catch (err) {
      console.error('Failed to copy SKU:', err);
    }
  };

  const getBadgeLabel = (source: string | undefined) => {
    switch (source) {
      case 'halilit': return 'Commercial';
      case 'official': return 'Official';
      case 'estimated': return 'Estimated';
      default: return null;
    }
  };

  if (!product && !jitState.isLoading && !jitState.error) {
    return (
      <div className="bg-zinc-950 min-h-screen p-4 flex flex-col items-center justify-center">
        <p className="text-white text-lg">Product not found</p>
        <button onClick={() => navigate(-1)} className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
          Back
        </button>
      </div>
    );
  }

  if (jitState.error) {
    return (
      <div className="bg-zinc-950 min-h-screen p-4 flex flex-col items-center justify-center">
        <div className="bg-red-800 text-white p-4 rounded flex items-center gap-2">
          <AlertTriangle size={20} />
          <span>Error loading product intelligence.</span>
          <button onClick={refetch} className="ml-4 px-2 py-1 bg-white text-red-700 rounded hover:bg-gray-200">Retry</button>
        </div>
      </div>
    );
  }

  if (jitState.isLoading || !product) {
    return (
      <div className="bg-zinc-950 min-h-screen p-4">
        <div className="md:grid md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <div className="bg-zinc-900 rounded-lg animate-pulse h-64 mb-4" />
            <div className="bg-zinc-800 rounded-full h-6 w-24 mb-2" />
            <div className="bg-zinc-800 rounded-full h-4 w-48 mb-2" />
          </div>
          <div className="md:col-span-2">
            <div className="bg-zinc-800 rounded-full h-8 w-64 mb-4" />
            <div className="bg-zinc-800 rounded-full h-4 w-full mb-2" />
            <div className="bg-zinc-800 rounded-full h-4 w-3/4 mb-2" />
          </div>
        </div>
      </div>
    );
  }

  const priceLabel = getBadgeLabel(product.data_trust?.price_source);
  const specsLabel = getBadgeLabel(product.data_trust?.specs_source);

  const price = (jitState.data as any)?.price ?? product.price;
  const priceEilat = (jitState.data as any)?.price_eilat ?? product.price_eilat;
  const name = (jitState.data as any)?.name ?? product.name;
  const brand = (jitState.data as any)?.brand ?? product.brand;
  const imageUrl = (jitState.data as any)?.image_url ?? product.image_url;

  return (
    <div className="bg-zinc-950 min-h-screen p-4">
      <div className="md:grid md:grid-cols-3 gap-6">

        {/* ── Left: Image + meta ─────────────────────────────────── */}
        <div className="md:col-span-1 space-y-3">
          {imageUrl
            ? <ImageWithFallback src={imageUrl} alt={name} className="rounded-xl w-full object-contain max-h-72" />
            : <div className="bg-zinc-800 rounded-xl h-64" />
          }
          <ProductImageCarousel images={product.image_gallery || []} />

          {/* SKU */}
          <div className="flex items-center justify-between bg-zinc-900 rounded-lg px-3 py-2">
            <div className="flex items-center gap-2">
              <span className="text-zinc-400 text-xs">SKU</span>
              <span className="text-white text-sm font-mono">{product.id}</span>
            </div>
            <button onClick={handleCopySKU} className="text-blue-400 hover:text-blue-300">
              {copied ? <Check size={14} /> : <ClipboardCopy size={14} />}
            </button>
          </div>

          {/* Pricing */}
          <div className="space-y-1">
            {price > 0
              ? <p className="text-white font-semibold">₪ {price.toLocaleString('he-IL')} <span className="text-zinc-500 text-xs font-normal">(IL)</span></p>
              : <p className="text-zinc-500 italic">Call for Price (IL)</p>
            }
            {priceEilat > 0 && (
              <p className="text-zinc-300 text-sm">₪ {priceEilat.toLocaleString('he-IL')} <span className="text-zinc-500 text-xs">(Eilat)</span></p>
            )}
            {priceLabel && <SourcingBadge source={(product.data_trust?.price_source ?? 'none') as any} label={priceLabel} />}
          </div>

          {/* Links */}
          <div className="space-y-1">
            {product.halilit_url && (
              <a href={product.halilit_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 text-sm">
                <ExternalLink size={14} /> Halilit Page
              </a>
            )}
            {product.official_url && (
              <a href={product.official_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-1.5 text-sky-400 hover:text-sky-300 text-sm">
                <ExternalLink size={14} /> Official Page
              </a>
            )}
          </div>
          {specsLabel && <SourcingBadge source={(product.data_trust?.specs_source ?? 'none') as any} label={specsLabel} />}
        </div>

        {/* ── Right: Tabs ────────────────────────────────────────── */}
        <div className="md:col-span-2">
          <div className="flex items-start justify-between mb-4 gap-2">
            <div>
              <h1 className="text-white text-2xl font-semibold leading-tight">{name}</h1>
              <p className="text-zinc-400 text-sm mt-0.5">{brand}</p>
            </div>
            <JITBadge productId={product.id} />
          </div>

          {/* Tab bar */}
          <div className="flex border-b border-zinc-700 mb-4">
            {(['overview', 'specs', 'ecosystem', 'reviews'] as const).map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={`py-2 px-4 capitalize text-sm transition-colors ${
                  activeTab === tab
                    ? 'border-b-2 border-blue-500 text-blue-400'
                    : 'text-zinc-400 hover:text-white'
                }`}>
                {tab}
              </button>
            ))}
          </div>

          {/* Overview */}
          {activeTab === 'overview' && (
            <div className="space-y-4">
              {product.description && <p className="text-zinc-200 leading-relaxed">{product.description}</p>}
              {(product.features?.length ?? 0) > 0 && (
                <div>
                  <h2 className="text-white font-semibold mb-2">Features</h2>
                  <ul className="list-disc list-inside text-zinc-300 space-y-1">
                    {product.features.map((f, i) => <li key={i}>{f}</li>)}
                  </ul>
                </div>
              )}
              {(product.pros?.length ?? 0) > 0 && (
                <div>
                  <h2 className="text-white font-semibold mb-2">Pros</h2>
                  <ul className="list-disc list-inside text-emerald-400 space-y-1">
                    {product.pros.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              )}
              {(product.cons?.length ?? 0) > 0 && (
                <div>
                  <h2 className="text-white font-semibold mb-2">Cons</h2>
                  <ul className="list-disc list-inside text-red-400 space-y-1">
                    {product.cons.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Specs table */}
          {activeTab === 'specs' && (
            <table className="text-sm text-zinc-300 w-full">
              <tbody>
                {Object.entries(product.specs || {}).map(([key, value]) => (
                  <tr key={key} className="border-b border-zinc-800">
                    <td className="py-2 pr-4 text-white font-medium whitespace-nowrap w-1/3">{key}</td>
                    <td className="py-2 text-zinc-300">{String(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {/* Ecosystem */}
          {activeTab === 'ecosystem' && <EcosystemTab productId={product.id} />}

          {/* Reviews */}
          {activeTab === 'reviews' && (
            <div className="space-y-3">
              {product.rating > 0 && (
                <p className="text-zinc-200">Rating: <span className="text-white font-semibold">{product.rating}/5</span>
                  {product.review_count > 0 && <span className="text-zinc-500 text-sm"> ({product.review_count} reviews)</span>}
                </p>
              )}
              {product.review_synthesis_summary && (
                <p className="text-zinc-300 leading-relaxed">{product.review_synthesis_summary}</p>
              )}
              {(product.real_world_insights?.length ?? 0) > 0 && (
                <div>
                  <h2 className="text-white font-semibold mb-2">Real-world Insights</h2>
                  <ul className="list-disc list-inside text-zinc-300 space-y-1">
                    {product.real_world_insights!.map((insight, i) => <li key={i}>{insight}</li>)}
                  </ul>
                </div>
              )}
              {product.review_sources && product.review_sources.length > 0 && (
                <p className="text-zinc-500 text-xs">Sources: {product.review_sources.join(', ')}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;
