import React from "react";
import { ConductorProduct } from "../../types";
import { CopySKUButton } from "./CopySKUButton";

interface ProductDetailHeaderProps {
  product: ConductorProduct | null;
  className?: string;
}

const StockBadge: React.FC<{ status: "IN STOCK" | "OUT OF STOCK" | "UNCONFIRMED" }> = ({
  status,
}) => {
  let bgColor = "";
  let textColor = "";
  let label = "";

  switch (status) {
    case "IN STOCK":
      bgColor = "bg-green-500";
      textColor = "text-white";
      label = "IN STOCK";
      break;
    case "OUT OF STOCK":
      bgColor = "bg-red-500";
      textColor = "text-white";
      label = "OUT OF STOCK";
      break;
    case "UNCONFIRMED":
      bgColor = "bg-amber-500";
      textColor = "text-gray-800";
      label = "UNCONFIRMED";
      break;
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${bgColor} ${textColor}`}
    >
      {label}
    </span>
  );
};

export const ProductDetailHeader: React.FC<ProductDetailHeaderProps> = ({
  product,
  className,
}) => {
  if (!product) {
    return null;
  }

  const stockStatus =
    product.stock === 0
      ? "OUT OF STOCK"
      : product.stock === null
        ? "UNCONFIRMED"
        : product.stock > 0
          ? "IN STOCK"
          : null;

  const showCallForPrice = product.price === null || product.price === 0;

  return (
    <header className={`flex items-center justify-between p-6 ${className}`}>
      <div>
        <h1 className="text-2xl font-semibold text-white">{product.name}</h1>
      </div>
      <div className="flex items-center space-x-2">
        {stockStatus && <StockBadge status={stockStatus} />}
        {showCallForPrice && (
          <>
            <span className="text-sm font-medium text-red-500">
              Call for Price
            </span>
            <CopySKUButton sku={product.sku} />
          </>
        )}
        {product.stock !== 0 && !showCallForPrice && product.price !== null && product.price > 0 && (
          <span className="text-white">
            ₪{product.price.toFixed(2)}
          </span>
        )}
      </div>
    </header>
  );
};