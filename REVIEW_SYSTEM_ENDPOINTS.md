# Review System - URL Endpoints & Access Guide

## 🌐 Available Endpoints

### View/Display Endpoints

#### 1. **View All Reviews for a Product**
```
URL: /review/product/<product_id>/reviews/
Method: GET
Auth Required: Yes (login_required)
Description: Display all reviews for a specific product with rating statistics
Response: product_reviews.html template
```

**Example:**
```
/review/product/1/reviews/
```

---

### Submission Endpoints

#### 2. **Add New Review**
```
URL: /review/product/<product_id>/review/add/
Method: GET (form display) / POST (submission)
Auth Required: Yes (login_required)
Description: Submit a new review for a product
Requirements:
  - User must be authenticated
  - User must have purchased the product (verified)
  - User cannot have already reviewed this product
Response GET: add_review.html form
Response POST: Redirect to product page
```

**Example:**
```
/review/product/1/review/add/
```

**Form Data (POST):**
```
rating: 5
title: "Amazing product!"
comment: "This product exceeded my expectations..."
```

---

### Edit/Update Endpoints

#### 3. **Edit Existing Review**
```
URL: /review/review/<review_id>/edit/
Method: GET (form display) / POST (submission)
Auth Required: Yes (login_required)
Description: Edit an existing review
Requirements:
  - User must be the review author
  - Review must exist
Response GET: edit_review.html form
Response POST: Redirect to product page
```

**Example:**
```
/review/review/42/edit/
```

**Form Data (POST):**
```
rating: 4
title: "Updated title"
comment: "Updated comment..."
```

---

### Delete Endpoints

#### 4. **Delete Review**
```
URL: /review/review/<review_id>/delete/
Method: GET (confirmation) / POST (deletion)
Auth Required: Yes (login_required)
Description: Delete a review (soft delete via is_active field)
Requirements:
  - User must be the review author
Response GET: delete_review.html confirmation
Response POST: Redirect to product page
```

**Example:**
```
/review/review/42/delete/
```

---

### Interaction Endpoints

#### 5. **Mark Review as Helpful/Not Helpful**
```
URL: /review/review/<review_id>/vote/
Method: POST (AJAX)
Auth Required: Yes (login_required)
Content-Type: application/x-www-form-urlencoded
Description: Vote on whether a review is helpful
Response: JSON
```

**Example:**
```
POST /review/review/42/vote/
vote_type=helpful
```

**Response:**
```json
{
  "success": true,
  "action": "added",
  "helpful_votes": 5
}
```

**Possible Actions:**
- `added` - Vote added
- `updated` - Vote changed
- `removed` - Vote removed

---

#### 6. **Report Review**
```
URL: /review/review/<review_id>/report/
Method: GET (form) / POST (submission)
Auth Required: Yes (login_required)
Description: Report an inappropriate review
Response GET: report_review.html form
Response POST: Redirect to product page
```

**Example:**
```
POST /review/review/42/report/
reason=Inappropriate+content
```

---

## 📱 Web Form Access

### From Product Detail Page
```
1. Visit: /products/{product-slug}/
2. Scroll to "Reviews" section
3. Click "View All Reviews" link → goes to endpoint #1
4. Or click "Write Review" → goes to endpoint #2
```

### Direct URLs for Review Operations

**Add Review for Product 1:**
```
/review/product/1/review/add/
```

**View All Reviews for Product 1:**
```
/review/product/1/reviews/
```

**Edit Review 42:**
```
/review/review/42/edit/
```

**Delete Review 42:**
```
/review/review/42/delete/
```

**Mark Review 42 as Helpful:**
```
/review/review/42/vote/
```

**Report Review 42:**
```
/review/review/42/report/
```

---

## 🔐 Authentication Requirements

All endpoints require user to be logged in:
```
Login URL: /accounts/login/
Redirect: Redirects to login if not authenticated
```

### Additional Requirements by Endpoint

| Endpoint | Auth | Purchase | Own Review |
|----------|------|----------|-----------|
| View Reviews | ✅ | ❌ | ❌ |
| Add Review | ✅ | ✅ | ❌ |
| Edit Review | ✅ | ❌ | ✅ |
| Delete Review | ✅ | ❌ | ✅ |
| Vote Review | ✅ | ❌ | ❌ |
| Report Review | ✅ | ❌ | ❌ |

---

## 💾 Database Queries Reference

### Get Average Rating for a Product
```python
from products.models import Product
product = Product.objects.get(id=1)
avg_rating = product.average_rating  # Returns float (0-5)
```

### Get Review Count for a Product
```python
from products.models import Product
product = Product.objects.get(id=1)
count = product.review_count  # Returns int
```

### Get All Reviews for a Product
```python
from review_system.models import Review
reviews = Review.objects.filter(
    product_id=1,
    is_active=True
).order_by('-created_at')
```

### Get User's Review for a Product
```python
from review_system.models import Review
review = Review.objects.get(
    user=request.user,
    product_id=1
)
```

### Get Helpful Votes for a Review
```python
from review_system.models import ReviewVote
helpful_count = ReviewVote.objects.filter(
    review_id=42,
    vote_type='helpful'
).count()
```

---

## 🎯 Common Use Cases

### Scenario 1: User Wants to Write a Review
```
1. User visits /products/product-slug/
2. Clicks "Reviews" tab
3. Clicks "Write Review" button
4. Redirected to /review/product/1/review/add/
5. Selects rating, enters title and comment
6. Clicks "Submit Review"
7. Redirected back to product page
8. Review appears in reviews list
```

### Scenario 2: User Wants to Edit Their Review
```
1. User visits /products/product-slug/
2. Clicks "Reviews" tab
3. Finds their review in the list
4. Clicks "Edit"
5. URL: /review/review/42/edit/
6. Updates rating, title, or comment
7. Clicks "Update Review"
8. Redirected back to product page
9. Changes are visible
```

### Scenario 3: User Marks a Review as Helpful
```
1. User views reviews on product page
2. Sees a helpful review
3. Clicks "Helpful" button (thumbs up)
4. AJAX request sent to /review/review/42/vote/
5. Vote count updates without page reload
6. User sees confirmation message
```

### Scenario 4: Admin Wants to Manage Reviews
```
1. Go to /admin/
2. Navigate to "Review System" → "Reviews"
3. See all reviews with filters
4. Can activate/deactivate (soft delete)
5. Can filter by rating, verified purchase, date
6. Can search by user email, product name, title
7. Can view and edit review details
```

---

## 🧪 Testing URLs

### Using cURL

**Get reviews for product 1:**
```bash
curl -b cookies.txt http://localhost:8000/review/product/1/reviews/
```

**Add a review (POST):**
```bash
curl -X POST \
  -b cookies.txt \
  -F "rating=5" \
  -F "title=Great product" \
  -F "comment=This product is amazing!" \
  http://localhost:8000/review/product/1/review/add/
```

**Vote on a review (AJAX):**
```bash
curl -X POST \
  -b cookies.txt \
  -d "vote_type=helpful" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  http://localhost:8000/review/review/1/vote/
```

---

## 📊 Admin Interface

### Admin URLs
```
Django Admin: /admin/
Review System Admin: /admin/review_system/review/
```

### Available Admin Actions
1. **View Reviews**
   - List all reviews
   - Filter by rating, date, verified status
   - Search by user, product, title

2. **Edit Review**
   - Change rating, title, comment
   - Toggle is_verified_purchase
   - Toggle is_active

3. **Manage Images**
   - Upload images inline
   - Add captions
   - Delete images

4. **View Votes**
   - See helpful/not helpful votes
   - Track vote history

---

## 🔗 URL Configuration File

**Location:** `review_system/urls.py`

```python
urlpatterns = [
    # View reviews
    path('product/<int:product_id>/reviews/', 
         views.product_reviews, 
         name='product_reviews'),
    
    # Add review
    path('product/<int:product_id>/review/add/', 
         views.add_review, 
         name='add_review'),
    
    # Edit review
    path('review/<int:review_id>/edit/', 
         views.edit_review, 
         name='edit_review'),
    
    # Delete review
    path('review/<int:review_id>/delete/', 
         views.delete_review, 
         name='delete_review'),
    
    # Vote on review
    path('review/<int:review_id>/vote/', 
         views.vote_review, 
         name='vote_review'),
    
    # Report review
    path('review/<int:review_id>/report/', 
         views.report_review, 
         name='report_review'),
]
```

**Included in:** `analytics_dashboard/urls.py`
```python
path('review/', include('review_system.urls', namespace='review_system'))
```

---

## 💡 Tips & Tricks

### Using URL Reversing in Templates
```django
<!-- View all reviews -->
<a href="{% url 'review_system:product_reviews' product.id %}">
    View All Reviews
</a>

<!-- Write review -->
<a href="{% url 'review_system:add_review' product.id %}">
    Write Review
</a>

<!-- Edit review -->
<a href="{% url 'review_system:edit_review' review.id %}">
    Edit
</a>

<!-- Delete review -->
<a href="{% url 'review_system:delete_review' review.id %}">
    Delete
</a>
```

### Getting Review URLs in Python
```python
from django.urls import reverse

# Get URL for product reviews
url = reverse('review_system:product_reviews', args=[product_id])

# Get URL to add review
url = reverse('review_system:add_review', args=[product_id])

# Get URL to edit review
url = reverse('review_system:edit_review', args=[review_id])
```

---

## 🚨 Error Handling

### Common Errors & Solutions

**404 Not Found - Product doesn't exist**
```
Request: /review/product/999/reviews/
Error: Product matching query does not exist
Solution: Verify product_id is correct
```

**403 Forbidden - User can't edit review**
```
Request: /review/review/42/edit/ (different user)
Error: User is not the review author
Solution: Only review author can edit
```

**400 Bad Request - Missing required fields**
```
POST data missing: rating, title, or comment
Error: Please fill in all required fields
Solution: Include all required form fields
```

**401 Unauthorized - User not logged in**
```
Request: /review/product/1/reviews/ (without login)
Error: Redirect to login page
Solution: Login first
```

---

## 📞 Quick Reference

| Action | URL | Method |
|--------|-----|--------|
| View reviews | `/review/product/{id}/reviews/` | GET |
| Add review | `/review/product/{id}/review/add/` | GET/POST |
| Edit review | `/review/review/{id}/edit/` | GET/POST |
| Delete review | `/review/review/{id}/delete/` | GET/POST |
| Vote helpful | `/review/review/{id}/vote/` | POST |
| Report review | `/review/review/{id}/report/` | GET/POST |

---

**That's everything you need to know about the review system endpoints!** ✨
