// Contract: Product Detail - Ethically Sourced Badge

export const PRODUCT_SOURCING_ENDPOINT = '/api/products/{product_id}/sourcing';

export type SourcingStatus = "Ethically Sourced" | "Partially Sourced" | "Unknown Sourcing";

export interface ProductSourcingResponse {
  status: SourcingStatus;
}

export interface ProductSourcingErrorResponse {
  detail: string;
}