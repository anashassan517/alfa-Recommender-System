// Function to load personalized recommendations
function loadPersonalizedRecommendations(userId) {
    fetch(`http://localhost:8088/api/recommend/${userId}/`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('personalizedRecommendations');
            if (data && data.length > 0) {
                container.innerHTML = '';
                
                data.forEach(product => {
                    const slide = document.createElement('div');
                    slide.className = 'swiper-slide';
                    slide.innerHTML = `
                        <div class="product-card">
                            <div class="product-image-wrapper">
                                <a href="${product.url}">
                                    <img src="${product.image}" class="product-image" alt="${product.name}">
                                </a>
                                <div class="quick-actions">
                                    <button class="action-icon add-to-cart" data-product-id="${product.id}">
                                        <i class="fas fa-shopping-cart"></i>
                                    </button>
                                    <button class="action-icon add-to-wishlist" data-product-id="${product.id}">
                                        <i class="fas fa-heart"></i>
                                    </button>
                                    <button class="action-icon quick-view" data-product-id="${product.id}">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="product-info">
                                <h3 class="product-title">${product.name}</h3>
                                <div class="product-price">
                                    <span class="original-price">PKR ${product.original_price}</span>
                                    <span class="current-price">PKR ${product.price}</span>
                                </div>
                                <a href="${product.url}" class="btn btn-view-details">View Details</a>
                            </div>
                        </div>
                    `;
                    container.appendChild(slide);
                });
                
                // Initialize swiper
                new Swiper('.recommended-swiper', {
                    slidesPerView: 1,
                    spaceBetween: 20,
                    navigation: {
                        nextEl: '.recommended-button-next',
                        prevEl: '.recommended-button-prev'
                    },
                    breakpoints: {
                        576: {
                            slidesPerView: 2
                        },
                        992: {
                            slidesPerView: 3
                        },
                        1200: {
                            slidesPerView: 4
                        }
                    },
                    grabCursor: true
                });
                
                // Apply cart button event handlers to new elements
                document.querySelectorAll('.quick-actions .add-to-cart').forEach(button => {
                    button.addEventListener('click', handleAddToCart);
                });
                
            } else {
                // Handle empty recommendations
                container.innerHTML = `
                    <div class="swiper-slide">
                        <div class="product-card text-center p-5">
                            <p>No recommendations available at the moment.</p>
                            <a href="/products/" class="btn btn-outline-danger mt-3">Browse Products</a>
                        </div>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            const container = document.getElementById('personalizedRecommendations');
            container.innerHTML = `
                <div class="swiper-slide">
                    <div class="product-card text-center p-5">
                        <p>Unable to load recommendations. Please try again later.</p>
                        <a href="/products/" class="btn btn-outline-danger mt-3">Browse Products</a>
                    </div>
                </div>
            `;
        });
}

// Function to handle add to cart clicks
function handleAddToCart(e) {
    e.preventDefault();
    const productId = this.getAttribute('data-product-id');
    
    // Show +1 animation
    const buttonRect = this.getBoundingClientRect();
    const plusOne = document.createElement('div');
    plusOne.className = 'add-to-cart-anim';
    plusOne.textContent = '+1';
    plusOne.style.left = `${buttonRect.left + buttonRect.width/2}px`;
    plusOne.style.top = `${buttonRect.top}px`;
    document.body.appendChild(plusOne);
    
    setTimeout(() => {
        plusOne.remove();
    }, 1000);
    
    // Add to cart AJAX call
    fetch('/api/cart/add/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: 1
        })
    })
    .then(response => response.json())
    .then(data => {
        const cartBadge = document.querySelector('.cart-badge');
        if (cartBadge) {
            cartBadge.textContent = data.cart_count;
        }
    })
    .catch(error => {
        console.error('Error adding to cart:', error);
    });
}

// Helper function to get cookie by name (for CSRF token)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 