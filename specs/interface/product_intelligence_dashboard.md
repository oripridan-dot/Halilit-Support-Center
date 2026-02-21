# Spec: Product Intelligence Dashboard

**Target:** ui/src/components/ProductIntelligenceDashboard.tsx

## Overview
This React component provides a dashboard interface for displaying key performance indicators (KPIs) and analytics related to products manufactured by the Halilit Dark Factory. The dashboard visualizes real-time production metrics, highlighting potential bottlenecks, quality control issues, and efficiency improvements. This data will be pulled from the existing production tracking system.

## Requirements
- The dashboard must display real-time data, updating at least every 5 seconds.
- The dashboard must present data visualizations for the following KPIs:
    - **Production Volume:** Number of units produced per hour.
    - **Defect Rate:** Percentage of defective units detected during quality control.
    - **Cycle Time:** Average time taken to produce one unit.
    - **Machine Utilization:** Percentage of time machines are actively running.
- The visualizations should be clear, concise, and easy to understand, using charts and graphs where appropriate (e.g., line chart for production volume over time, bar chart for defect rates by machine).
- The dashboard should provide options to filter data by:
    - Product type
    - Production line
    - Date/time range
- The dashboard should highlight anomalies or potential issues, such as a sudden drop in production volume or a spike in defect rates.  These should be clearly flagged with visual cues (e.g., color-coded alerts).
- The dashboard should be responsive and adapt to different screen sizes.
- Data fetching should be optimized to minimize server load and network traffic.
- The component must be implemented using React 18, TypeScript, and Tailwind CSS.

## Data Contract
**Props:** None (data is fetched from the API)

**API Endpoint:** `/api/product_intelligence`

**Request:** (GET)

**Response (JSON):**
```typescript
interface ProductIntelligenceData {
  productionVolume: {
    time: string; // ISO 8601 timestamp
    value: number;
  }[];
  defectRate: {
    machineId: string;
    value: number;
  }[];
  cycleTime: {
    productType: string;
    value: number;
  }[];
  machineUtilization: {
    machineId: string;
    value: number;
  }[];
  anomalies: {
    type: "productionVolume" | "defectRate";
    message: string;
    timestamp: string; // ISO 8601 timestamp
  }[];
  availableProducts: string[]; // List of product types for filtering
  availableProductionLines: string[]; // List of production lines for filtering
}
```

## Behavior Scenarios
- **Scenario:** Initial Load
  - Input: Component mounts.
  - Outcome:
    - Data is fetched from `/api/product_intelligence`.
    - Loading indicators are displayed while data is loading.
    - Once data is loaded, the KPIs and visualizations are rendered.
    - Dropdown filters for product types and production lines are populated from `availableProducts` and `availableProductionLines` in the response.
- **Scenario:** Data Refresh
  - Input: Timer triggers a data refresh (every 5 seconds).
  - Outcome:
    - Data is re-fetched from `/api/product_intelligence`.
    - The KPIs and visualizations are updated with the new data.
    - The UI provides a visual indication that the data has been updated.
- **Scenario:** Filtering by Product Type
  - Input: User selects a product type from the filter dropdown.
  - Outcome:
    - The `productionVolume`, `defectRate`, `cycleTime`, and `machineUtilization` data are filtered to show only data related to the selected product type.
    - The visualizations are updated to reflect the filtered data. A query parameter for `productType` is added to the GET request to `/api/product_intelligence`.
- **Scenario:** Filtering by Production Line
  - Input: User selects a production line from the filter dropdown.
  - Outcome:
    - The `productionVolume`, `defectRate`, `cycleTime`, and `machineUtilization` data are filtered to show only data related to the selected production line.
    - The visualizations are updated to reflect the filtered data. A query parameter for `productionLine` is added to the GET request to `/api/product_intelligence`.
- **Scenario:** Anomaly Detected
  - Input: The API returns an `anomaly` object in the response.
  - Outcome:
    - A visual alert is displayed on the dashboard, highlighting the anomaly and its timestamp. The alert should be prominently displayed, perhaps using a red background or a flashing icon. The anomaly type and message from the API response are used to generate the alert message.

## Out of Scope
- User authentication and authorization.
- Historical data analysis and reporting.
- Detailed machine-level diagnostics.
- Configuration of data refresh interval (it's fixed at 5 seconds).
- Custom chart types or visualization libraries beyond basic charting capabilities (e.g., Recharts or similar).
- Defining or implementing the `/api/product_intelligence` backend endpoint (that is specified elsewhere).
