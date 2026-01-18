# Linear Search Implementation for Product Search

## Overview
A basic product search functionality has been implemented using **linear search algorithm** as per requirements. The implementation searches through all products by iterating one by one and comparing the search keyword only with the product name.

## Implementation Details

### Algorithm: Linear Search
The search works by:
1. **Fetching all products** from the database once (not using database filtering)
2. **Converting the query to lowercase** for case-insensitive comparison
3. **Looping through each product** sequentially
4. **Comparing the search keyword** only with the product name
5. **Adding matches** to a results list
6. **Displaying results** on the search results page

### Code Location
**File:** [dashboard/views.py](dashboard/views.py#L87-L130)

**Function:** `search_products(request)`

### How It Works

```python
# LINEAR SEARCH: Loop through all products one by one
# This algorithm checks each product name sequentially
query_lower = query.lower()  # Convert search query to lowercase for case-insensitive comparison

for product in all_products:
    # Compare the search keyword only with the product name (case-insensitive)
    if query_lower in product.name.lower():
        matched_products.append(product)
```

### Key Features

✅ **Case-insensitive search** - Handles "Cream", "CREAM", "cream" the same way
✅ **Searches only product names** - Not descriptions, brands, or categories
✅ **Simple for loop** - No complex queries or libraries
✅ **Substring matching** - Finds keywords anywhere in the product name
✅ **No database filtering** - All products fetched, then searched in Python
✅ **Shows "No products found"** - Clear message when no matches exist
✅ **Result count** - Displays how many products matched

### Search Results Template
**File:** [templates/dashboard/search_results.html](templates/dashboard/search_results.html)

Features:
- Displays matched products in a grid layout
- Shows product name, brand, and price
- Links to detailed product pages
- "No products found" message when search yields no results
- Result count for successful searches

### Search Form (Navbar)
The existing navbar search form in [templates/base.html](templates/base.html#L44-L52) remains unchanged:
```html
<form class="d-flex me-4" method="GET" action="{% url 'dashboard:search_products' %}">
    <div class="input-group">
        <input class="form-control border-0" type="search" name="q" placeholder="Find your perfect match...">
        <button class="btn btn-outline-primary border-0" type="submit">
            <i class="fas fa-search"></i>
        </button>
    </div>
</form>
```

### URL Configuration
**File:** [dashboard/urls.py](dashboard/urls.py#L17)
```python
path('search/', views.search_products, name='search_products'),
```

## Example Usage

1. User enters "Moisturizer" in the navbar search box
2. Form submits to `http://localhost:8000/search/?q=Moisturizer`
3. `search_products` view:
   - Fetches all active products
   - Loops through each product
   - Checks if "moisturizer" (lowercase) is in product.name (lowercase)
   - Returns matching products
4. Results displayed in search_results.html page

## Limitations & Constraints (By Design)

❌ **No database filtering** - Linear search not optimized for large datasets
❌ **No wildcard support** - Simple substring matching only
❌ **Single field search** - Only searches product names
❌ **No advanced filters** - Category, brand, price filters removed (as per requirements)
❌ **No external libraries** - Pure Python loop implementation

## Time Complexity

- **Time:** O(n) where n = number of products
- **Space:** O(m) where m = number of matching products

## Testing the Search

1. Go to http://localhost:8000
2. Use the search bar in the navbar
3. Enter a product name (or partial name)
4. Click the search button
5. View results on the search results page

### Example Searches:
- "Serum" - finds products with "serum" in the name
- "beauty" - finds products with "beauty" in the name
- "cream" - finds skincare creams
- "xyz" - shows "No products found" message

---

**Implementation Date:** January 18, 2026
**Algorithm:** Linear Search (Sequential Scan)
**Complexity:** O(n) time, O(1) space for the search loop itself
