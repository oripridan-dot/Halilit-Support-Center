// Contract: Integrate Ethically Sourcing Status into Product Detail View

export const GET_PRODUCT_SOURCING_STATUS_PATH = '/api/products/{product_id}/sourcing';

export type SourcingStatus = "Ethically Sourced" | "Partially Sourced" | "Unknown Sourcing";

export interface GetProductSourcingStatusResponse {
  status: SourcingStatus;
}