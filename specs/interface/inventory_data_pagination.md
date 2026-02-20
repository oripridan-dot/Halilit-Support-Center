# Spec: Inventory Data Pagination
**Target:** src/components/InventoryTable/InventoryTable.tsx

## Overview
This component provides a paginated view of inventory data retrieved from a backend API. It displays inventory items in a tabular format with controls for navigating between pages. It is designed to be used within the Halilit Support Center's dark factory interface.

## Requirements
- Display inventory data in a tabular format, with columns for item ID, item name, quantity, location, and last updated timestamp.
- Implement pagination to handle large datasets, displaying a fixed number of items per page.
- Provide UI controls (previous/next buttons and page number indicator) for navigating between pages.
- Fetch inventory data from a specified API endpoint, including parameters for page number and page size.
- Handle loading state while fetching data, displaying a loading indicator.
- Handle error state when fetching data fails, displaying an error message.
- Use a dark theme (Tailwind CSS slate-900 background, blue-500 accent).
- Allow customization of the page size through a prop.
- Support sorting by column.

## Data Contract

**Input Props:**

```typescript
interface InventoryTableProps {
  pageSize: number; // Number of items to display per page.
  apiUrl: string; // API Endpoint to fetch inventory data from (e.g., "/api/inventory").
}
```

**API Request:**

```
GET /api/inventory?page={pageNumber}&page_size={pageSize}&sort_by={column}&sort_order={asc|desc}
```

**API Response:**

```json
{
  "total_items": 100,
  "total_pages": 10,
  "current_page": 1,
  "page_size": 10,
  "items": [
    {
      "item_id": "HAL-001",
      "item_name": "Gearbox Assembly",
      "quantity": 50,
      "location": "Warehouse A",
      "last_updated": "2024-10-27T10:00:00Z"
    },
    {
      "item_id": "HAL-002",
      "item_name": "Robotic Arm",
      "quantity": 10,
      "location": "Production Line 1",
      "last_updated": "2024-10-27T12:30:00Z"
    }
    // ... more items
  ]
}
```

```typescript
interface InventoryItem {
  item_id: string;
  item_name: string;
  quantity: number;
  location: string;
  last_updated: string; // ISO 8601 date string
}

interface InventoryResponse {
  total_items: number;
  total_pages: number;
  current_page: number;
  page_size: number;
  items: InventoryItem[];
}
```

## Behavior Scenarios

- **Scenario: Initial Load**
  - Input: Component mounts with `pageSize=10`, `apiUrl="/api/inventory"`
  - Outcome:
    - A loading indicator is displayed.
    - An API request is made to `/api/inventory?page=1&page_size=10&sort_by=&sort_order=asc`.
    - Once data is received, the loading indicator is removed, and the first 10 inventory items are displayed in the table.
    - Pagination controls show "Page 1 of [total_pages]".  "Previous" button is disabled. "Next" is enabled if current_page < total_pages.

- **Scenario: Navigate to Next Page**
  - Input: User clicks the "Next" button on page 1.
  - Outcome:
    - A loading indicator is displayed.
    - An API request is made to `/api/inventory?page=2&page_size=10&sort_by=&sort_order=asc`.
    - Once data is received, the loading indicator is removed, and inventory items 11-20 are displayed in the table.
    - Pagination controls show "Page 2 of [total_pages]". "Previous" button is enabled. "Next" button is enabled if current_page < total_pages.

- **Scenario: Navigate to Previous Page**
  - Input: User clicks the "Previous" button on page 2.
  - Outcome:
    - A loading indicator is displayed.
    - An API request is made to `/api/inventory?page=1&page_size=10&sort_by=&sort_order=asc`.
    - Once data is received, the loading indicator is removed, and the first 10 inventory items are displayed in the table.
    - Pagination controls show "Page 1 of [total_pages]". "Previous" button is disabled. "Next" button is enabled.

- **Scenario: API Error**
  - Input: API request to `/api/inventory?page=1&page_size=10&sort_by=&sort_order=asc` returns a 500 error.
  - Outcome:
    - The loading indicator is replaced with an error message: "Failed to load inventory data. Please try again later.".

- **Scenario: Empty Inventory**
  - Input: The API returns `{"total_items": 0, "total_pages": 0, "current_page": 1, "page_size": 10, "items": []}`.
  - Outcome:
    - The table displays a message: "No inventory items found."
    - Pagination controls are hidden or disabled.

- **Scenario: Sort by Item Name (Ascending)**
  - Input: User clicks the "Item Name" column header.
  - Outcome:
    - A loading indicator is displayed.
    - An API request is made to `/api/inventory?page=1&page_size=10&sort_by=item_name&sort_order=asc`.
    - The table is re-rendered with the inventory items sorted by item name in ascending order. The "Item Name" column header displays a visual cue indicating the sorting (e.g. an up arrow).

- **Scenario: Sort by Item Name (Descending)**
  - Input: User clicks the "Item Name" column header again (after sorting ascending).
  - Outcome:
    - A loading indicator is displayed.
    - An API request is made to `/api/inventory?page=1&page_size=10&sort_by=item_name&sort_order=desc`.
    - The table is re-rendered with the inventory items sorted by item name in descending order. The "Item Name" column header displays a visual cue indicating the sorting (e.g. a down arrow).

## Out of Scope
- Implementing the `/api/inventory` endpoint itself.
- Advanced filtering or searching capabilities.
- Real-time updates to the inventory data.
- User authentication and authorization.
