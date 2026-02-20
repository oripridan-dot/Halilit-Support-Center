// Contract: Ethically Sourced Status in Product Detail View

export const ETHICAL_SOURCING_ENDPOINT = '/api/products/{product_id}/sourcing';

export type SourcingStatus = "Ethically Sourced" | "Partially Sourced" | "Unknown Sourcing";

export interface SourcingResponse {
  status: SourcingStatus;
}

export interface SourcingErrorResponse {
  detail: string;
}