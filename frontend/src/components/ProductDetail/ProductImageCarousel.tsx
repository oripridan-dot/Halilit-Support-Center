import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

interface Image {
  url: string;
}

interface ImageResponse {
  images: Image[];
}

const ProductImageCarousel: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    const fetchImages = async () => {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/products/${id}/images`);
        if (response.status === 200) {
          const data: ImageResponse = await response.json();
          setImages(data.images);
        } else if (response.status === 204) {
          setImages([]);
        } else {
          const errorData = await response.json();
          setError(errorData.detail || "Failed to load images");
        }
      } catch (err: any) {
        setError(err.message || "Failed to load images");
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [id]);

  const goToPrevImage = () => {
    setCurrentImageIndex((prevIndex) =>
      prevIndex === 0 ? images.length - 1 : prevIndex - 1,
    );
  };

  const goToNextImage = () => {
    setCurrentImageIndex((prevIndex) =>
      prevIndex === images.length - 1 ? 0 : prevIndex + 1,
    );
  };

  if (loading) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-slate-900">
        <span className="loading loading-spinner text-blue-500"></span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-slate-900 text-red-500">
        {error}
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="w-full h-64 flex items-center justify-center bg-slate-900 text-white">
        No images available
      </div>
    );
  }

  return (
    <div className="relative w-full h-64 bg-slate-900">
      <img
        src={images[currentImageIndex].url}
        alt={`Product Image ${currentImageIndex + 1}`}
        className="w-full h-full object-contain"
        onError={(e) => {
          (e.target as HTMLImageElement).src = "/placeholder.png";
        }}
      />
      {images.length > 1 && (
        <>
          <button
            onClick={goToPrevImage}
            className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-slate-700/50 hover:bg-slate-700 text-white px-2 py-1 rounded-r-md"
          >
            &#10094;
          </button>
          <button
            onClick={goToNextImage}
            className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-slate-700/50 hover:bg-slate-700 text-white px-2 py-1 rounded-l-md"
          >
            &#10095;
          </button>
        </>
      )}
    </div>
  );
};

export default ProductImageCarousel;
