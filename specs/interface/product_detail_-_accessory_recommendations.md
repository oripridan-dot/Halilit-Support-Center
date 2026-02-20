# Spec: Product Detail - Accessory Recommendations

**Version:** 1.0
**Component:** `frontend/src/components/ProductDetail/AccessoryRecommendations.tsx`

## Purpose
To display a list of recommended accessories for a given product on the Product Detail page. This directly supports the "Maximize Attachment Rate" business goal by making it easy for operators to upsell accessories. If no accessories are available, a clear prompt is displayed.

## Requirements
1.  **Data Source:** Fetch accessory data from the `/api/products/{product_id}/accessories` endpoint.
2.  **Loading State:** Display a loading indicator (e.g., skeleton loaders) while fetching data.
3.  **Error Handling:** Display an error message if the API request fails.
4.  **Display Accessories:** If accessories are available, display them in a horizontal carousel.
5.  **Accessory Card:** Each accessory should be displayed as a card with:
    -   A thumbnail image
    -   The product name
    -   The product price (formatted)
6.  **Navigation:** Clicking an accessory card should navigate the user to the Product Detail page for that accessory. Use `useNavigationStore().goToProduct(accessory.id)`.
7.  **No Accessories Message:** If no accessories are available (API returns an empty list), display the message: "No verified accessories available. Check related products or official brand resources for suggestions to manually add." in a visually distinct manner.
8.  **Dark Theme Styling:** Use Tailwind CSS to style the component, adhering to the dark theme (slate-900 background, blue-500 accents).
9.  **Responsiveness:** The component should be responsive and adapt to different screen sizes.
10. **Verified Badge:** Show a "Verified" badge on the Accessory card.

## Data Contract

**API Endpoint:** `/api/products/{product_id}/accessories` (GET)

**Request:**
*   `product_id` (path parameter): The ID of the product for which to retrieve accessories.

**Response (Success - 200 OK):**

```json
{
  "accessories": [
    {
      "id": "string",
      "name": "string",
      "imageUrl": "string",
      "price": "number | null"
    },
    ...
  ]
}
```

**Response (No Accessories - 200 OK, Empty Array):**

```json
{
  "accessories": []
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "detail": "string" // Error message
}
```

**TypeScript Interface:**

```typescript
interface Accessory {
    id: string;
    name: string;
    imageUrl: string;
    price: number | null;
}

interface AccessoriesResponse {
    accessories: Accessory[];
}
```

## Behavior Scenarios

1.  **Scenario:** API returns accessories.
    *   Input: API returns a list of accessory objects.
    *   Outcome: The accessories are displayed in a horizontal carousel, each with a thumbnail, name, price, and "Verified" badge.
2.  **Scenario:** API returns no accessories.
    *   Input: API returns `{ accessories: [] }`.
    *   Outcome: The message "No verified accessories available. Check related products or official brand resources for suggestions to manually add." is displayed.
3.  **Scenario:** API returns an error.
    *   Input: API returns a 500 error.
    *   Outcome: An error message is displayed.
4.  **Scenario:** The component is loading.
    *   Input: The API request is in progress.
    *   Outcome: A loading indicator is displayed.
5. **Scenario:** Clicking an accessory.
    * Input: User clicks a card for accessory with `id: "ACC123"`.
    * Outcome: User navigates to the Product Detail page for `ACC123`.

## Stitch UI Prompt

```
You are Google Stitch, Dark Factory Edition. Your job is to generate a React component in TypeScript with Tailwind CSS, using the specified data slots and dark mode styles.

Component: Accessory Recommendations Carousel

Objective: Display a horizontal carousel of accessory recommendations. If no accessories are available, display a specific prompt to the operator.

Layout: Use a horizontal flexbox layout for the carousel. If there are no accessories, display a full-width alert message.

Data Slots:

- accessories: An array of objects, each with the following properties:
    - id: string (Product ID)
    - name: string (Product Name)
    - imageUrl: string (URL of the thumbnail image)
    - price: number | null (Price of the accessory, can be null if Call for Price)
- isLoading: boolean (Indicates if the data is loading)
- error: string | null (Error message, if any)

Visual Style:

- Dark mode with Tailwind CSS.
- Background: slate-900
- Text: zinc-300 for regular text, blue-500 for links and interactive elements.
- Borders: zinc-700 for dividers.
- Carousel: Horizontal scrolling with visible navigation arrows.
- Card:
    - Background: slate-800
    - Border: zinc-700
    - Padding: p-4
    - Shadow: shadow-md
- "Verified" Badge:
    - bg-green-500 text-white px-2 py-1 rounded-md text-xs
- No Accessories Message:
    - bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative

Component Hierarchy:

1.  Container (Flexbox, Horizontal Carousel):
    -   If isLoading: Display skeleton loaders.
    -   If error: Display error message.
    -   If accessories.length > 0:
        -   Map over accessories array:
            -   Accessory Card (see Card style above)
                -   Image (with placeholder on error)
                -   Name (text-lg font-semibold)
                -   Price (if price !== null, format as currency; otherwise, display "Call for Price")
                - "Verified" Badge
    -   Else:
        -   Display "No verified accessories available. Check related products or official brand resources for suggestions to manually add." message.

Spacing:

-   Carousel items: space-x-4
-   Card content: space-y-2

Specific Tailwind CSS tokens used elsewhere in Operator Console:
- slate-900 for primary background
- zinc-300 for primary text
- zinc-700 for borders
- blue-500 for interactive elements
- green-500 for "Verified" badge background
- amber-100 for "No Accessories" message background
- amber-400 for "No Accessories" message border
- amber-700 for "No Accessories" message text
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
