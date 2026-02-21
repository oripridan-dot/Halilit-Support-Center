# Spec: Enhance ProductDetailView with Skeleton and Ecosystem Tab
**Version:** 1.1
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## Purpose

Enhance the Product Detail View with a detailed skeleton UI while data is loading and display the Ecosystem Tab, and Accessory Recommendations. This addresses the "Speed of Service" business goal by providing immediate feedback to the user and the "Maximize Attachment Rate" business goal by displaying related products and integrations.

## Requirements

1. **Replace Loading Spinner:** Replace the existing loading spinner with the `SkeletonProductDetail` component from `frontend/src/components/SkeletonProductDetail.tsx`.
2. **Render Ecosystem Tab:** Integrate the `<EcosystemTab>` component into the `ProductDetailView`. Pass the `productId` to the `EcosystemTab` component. The tab must include a title: `Related Products and Integrations`.
3. **Render Accessory Recommendations:** Integrate the `<AccessoryRecommendations>` component into the `ProductDetailView`. Pass the `productId` to the `AccessoryRecommendations` component. The section must include a title: `Verified Accessories`.
4. **Conditional Rendering:**
    - Display the `SkeletonProductDetail` component while `isLoading` is true.
    - Display the actual product details, `<EcosystemTab>`, and `<AccessoryRecommendations>` only when `isLoading` is false, no `error`, and `product` is available.
    - Display error message when there is an `error`.
    - Display a "Product not found" message when `product` is not available.

5. **Layout and Styling:** Ensure the `SkeletonProductDetail`, `<EcosystemTab>`, and `<AccessoryRecommendations>` components are correctly styled and integrated into the overall layout of the `ProductDetailView`, maintaining the dark theme (slate-900 background, blue-500 accents).

6. **Ecosystem Tab and Accessory Recommendations Placement:** Place the `<EcosystemTab>` component below the product information and image, with the `<AccessoryRecommendations>` component right above the Ecosystem tab.

## Stitch UI Prompt
```text
// Target Component: ProductDetailView
// Description: The main Product Detail view, including a skeleton loading state, product information, accessory recommendations, and an ecosystem tab.
// Layout: Bento Grid
// Visual Style: Dark mode, Tailwind CSS, slate-900 background, blue-500 accents

<BentoGrid columns=2 gap=4 bg-slate-900 p=4 min-h=screen>

  // Loading State (Skeleton)
  <Conditional condition=isLoading>
    <SkeletonProductDetail colSpan=2 />
  </Conditional>

  // Error State
  <Conditional condition=!isLoading && error>
    <Alert variant=error colSpan=2>{error}</Alert>
  </Conditional>

  // Product Not Found State
  <Conditional condition=!isLoading && !error && !product>
    <Text color=zinc-400 colSpan=2>Product not found.</Text>
  </Conditional>

  // Product Details (when data is loaded)
  <Conditional condition=!isLoading && !error && product>

    // Header (Product Name, Stock Status, Call for Price)
    <Header colSpan=2>
      <ProductName>{product.name}</ProductName>
      <StockStatus status={product.stock} />
      <CallForPrice price={product.price} sku={product.sku} />
    </Header>

    // Product Image
    <ImageWithFallback src={product.image_url} alt={product.name} rounded=lg colSpan=1 rowSpan=2 />

    // Product Description
    <ProductDescription colSpan=1>{product.description}</ProductDescription>

    // Accessory Recommendations (Carousel)
    <AccessoryRecommendations productId={product.id} colSpan=2 title="Verified Accessories" />

    // Ecosystem Tab (Related Products and Integrations)
    <EcosystemTab productId={product.id} colSpan=2 title="Related Products and Integrations" />

  </Conditional>
</BentoGrid>

// Sub-Components (define their styles and data slots)

<SkeletonProductDetail>
  // This component should mimic the entire layout, using shimmer animations for placeholders.
</SkeletonProductDetail>

<Alert>
  // Red alert box for error messages.
  <Text>{errorMessage}</Text>
</Alert>

<Header>
  // Header region for product name and status indicators.
  <ProductName>{productName}</ProductName>
  <StockStatus>{stockStatus}</StockStatus>
  <CallForPrice>{callForPrice}</CallForPrice>
</Header>

<ProductName>
  // Large, bold product name.
  <Text size=2xl font=bold color=white>{productName}</Text>
</ProductName>

<StockStatus>
  // Badge indicating stock status (In Stock, Out of Stock, Unconfirmed).
  <Badge color={stockColor}>{stockStatus}</Badge>
</StockStatus>

<CallForPrice>
  // Label and button for "Call for Price" items.
  <Text color=red-500>Call for Price</Text>
  <CopySkuButton sku={sku} />
</CallForPrice>

<ImageWithFallback>
  // Component to display the product image, with a fallback image if the primary image fails to load.
  <img src={imageUrl} alt={altText} rounded=lg />
</ImageWithFallback>

<ProductDescription>
  // Paragraph displaying the product description.
  <Text color=zinc-400>{productDescription}</Text>
</ProductDescription>

<AccessoryRecommendations>
  // Horizontal carousel displaying accessory recommendations.
   <Title>{title}</Title>
  <Carousel>
    <AccessoryCard>{accessoryDetails}</AccessoryCard>
  </Carousel>
</AccessoryRecommendations>

<EcosystemTab>
  // Tab displaying related products and integrations.
  <TabTitle>{title}</TabTitle>
  <RelatedProducts>{relatedProducts}</RelatedProducts>
  <Integrations>{integrations}</Integrations>
</EcosystemTab>

// Data Slots (examples)
// productName: "Example Product Name"
// stockStatus: "In Stock"
// stockColor: "green"
// callForPrice: true
// imageUrl: "https://example.com/product.jpg"
// productDescription: "This is a sample product description."
// accessoryDetails: "Accessory Name, Price, Image"
// relatedProducts: "Related Product 1, Related Product 2"
// integrations: "Integration 1, Integration 2"

```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
