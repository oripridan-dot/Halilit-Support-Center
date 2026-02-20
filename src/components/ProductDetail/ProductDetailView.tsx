import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Document,
  TroubleshootingGuide,
import {
  MagnifyingGlassIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from 'lucide-react';

interface ProductInfoProps {
  name: string;
  description: string;
  serialNumber?: string | null;
}

const ProductInfo: React.FC<ProductInfoProps> = ({
  name,
  description,
  serialNumber,
}) => {
  return (
    <div className="mb-6">
      <h2 className="text-2xl font-semibold text-zinc-200">{name}</h2>
      <p className="text-zinc-400 mt-2">{description}</p>
      {serialNumber !== null && serialNumber !== undefined && (
        <p className="text-zinc-400 mt-2">
          Serial Number: {serialNumber || 'Not Available'}
        </p>
      )}
    </div>
  );
};

interface ProductDocumentsProps {
  documents: Document[];
}

const ProductDocuments: React.FC<ProductDocumentsProps> = ({ documents }) => {
  if (!documents || documents.length === 0) {
    return (
      <div className="mt-4">
        <p className="text-zinc-400">No documents available.</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold text-zinc-200 mb-2">Documents</h3>
      <ul>
        {documents.map((doc) => (
          <li key={doc.id} className="mb-2">
            <a
              href={doc.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 flex items-center"
            >
              <DocumentTextIcon size={16} className="mr-2" />
              {doc.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
};

interface ProductTroubleshootingProps {
  troubleshootingGuides: TroubleshootingGuide[];
}

const ProductTroubleshooting: React.FC<ProductTroubleshootingProps> = ({
  troubleshootingGuides,
}) => {
  if (!troubleshootingGuides || troubleshootingGuides.length === 0) {
    return (
      <div className="mt-4">
        <p className="text-zinc-400">No troubleshooting guides available.</p>
      </div>
    );
  }

  return (
    <div className="mt-6">
      <h3 className="text-lg font-semibold text-zinc-200 mb-2">
        Troubleshooting Guides
      </h3>
      {troubleshootingGuides.map((guide) => (
        <div key={guide.id} className="mb-4">
          <h4 className="text-zinc-200 font-medium">{guide.title}</h4>
          <ul className="list-decimal pl-5 mt-1 text-zinc-400">
            {guide.steps.map((step, index) => (
              <li key={index} className="mb-1">
                {step}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

const ProductDetailView: React.FC = () => {
  const { productId } = useParams<{ productId: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!productId) {
        setError('Product ID not provided.');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const response = await fetch(`/api/products/${productId}`);
        if (!response.ok) {
          if (response.status === 404) {
            setError('Product not found');
          } else {
            setError(
              'Failed to load product details. Please try again later.',
            );
          }
          setProduct(null);
          setLoading(false);
          return;
        }

        const data: Product = await response.json();
        setProduct(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load product details. Please try again later.');
        setProduct(null);
        setLoading(false);
      }
    };

    fetchProduct();
  }, [productId]);

  if (loading) {
    return (
      <div className="bg-slate-900 min-h-screen p-4">
        <div className="max-w-3xl mx-auto">
          <div className="animate-pulse bg-zinc-800 rounded-md p-4 mb-4">
            <div className="h-6 bg-zinc-700 rounded w-2/3" />
            <div className="h-4 bg-zinc-700 rounded mt-2 w-5/6" />
            <div className="h-4 bg-zinc-700 rounded mt-2 w-4/6" />
          </div>
          <div className="animate-pulse bg-zinc-800 rounded-md p-4 mb-4">
            <div className="h-4 bg-zinc-700 rounded w-1/2" />
            <div className="h-4 bg-zinc-700 rounded mt-2 w-3/4" />
            <div className="h-4 bg-zinc-700 rounded mt-2 w-2/3" />
          </div>
          <div className="animate-pulse bg-zinc-800 rounded-md p-4">
            <div className="h-4 bg-zinc-700 rounded w-1/2" />
            <div className="h-4 bg-zinc-700 rounded mt-2 w-3/4" />
            <div className="h-4 bg-zinc-700 rounded mt-2 w-2/3" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-slate-900 min-h-screen flex items-center justify-center">
        <div className="text-center p-4 bg-zinc-800 rounded-md max-w-md">
          <ExclamationTriangleIcon size={48} className="mx-auto text-yellow-500 mb-2" />
          <p className="text-zinc-200 font-semibold">{error}</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return null; // Or render an empty state/message
  }

  return (
    <div className="bg-slate-900 min-h-screen p-4">
      <div className="max-w-3xl mx-auto">
        <ProductInfo
          name={product.name}
          description={product.description}
          serialNumber={product.serial_number}
        />
        <ProductDocuments documents={product.documents || []} />
        <ProductTroubleshooting
          troubleshootingGuides={product.troubleshooting_guides || []}
        />
      </div>
    </div>
  );
};

export default ProductDetailView;