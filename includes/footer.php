<!-- Footer -->
    <footer class="footer mt-5">
        <div class="container">
            <div class="row">
                <div class="col-md-3">
                    <h5><i class="fas fa-bolt"></i> Volt3dge</h5>
                    <p>Your premium destination for 3D printing services and custom models.</p>
                </div>
                <div class="col-md-3">
                    <h5>Services</h5>
                    <ul class="list-unstyled">
                        <li><a href="products.php" class="text-light">3D Printing</a></li>
                        <li><a href="stl_upload.php" class="text-light">Custom STL Printing</a></li>
                        <li><a href="products.php" class="text-light">Product Catalog</a></li>
                    </ul>
                </div>
                <div class="col-md-3">
                    <h5>Quick Links</h5>
                    <ul class="list-unstyled">
                        <li><a href="index.php" class="text-light">Home</a></li>
                        <li><a href="products.php" class="text-light">Products</a></li>
                        <li><a href="my_stl_files.php" class="text-light">My STL Files</a></li>
                    </ul>
                </div>
                <div class="col-md-3">
                    <h5>Contact Info</h5>
                    <p><i class="fas fa-envelope"></i> info@volt3dge.com</p>
                    <p><i class="fas fa-phone"></i> +917828900162</p>
                </div>
            </div>
            <hr class="my-4">
            <div class="text-center">
                <p>&copy; 2025 Volt3dge. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Add to cart with AJAX
        function addToCart(productId) {
            fetch('cart_actions.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'action=add&product_id=' + productId + '&csrf_token=' + document.querySelector('[name="csrf_token"]').value
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update cart badge
                    const cartBadge = document.querySelector('.cart-badge');
                    if (cartBadge) {
                        cartBadge.textContent = data.cart_items;
                    } else if (data.cart_items > 0) {
                        // Create badge if it doesn't exist
                        const cartLink = document.querySelector('a[href*="cart"]');
                        const badge = document.createElement('span');
                        badge.className = 'cart-badge';
                        badge.textContent = data.cart_items;
                        cartLink.appendChild(badge);
                    }
                    
                    showMessage('Product added to cart!', 'success');
                } else {
                    showMessage(data.message || 'Error adding product to cart', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('Error adding product to cart', 'danger');
            });
        }
        
        function showMessage(message, type) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv, container.firstChild);
                
                // Auto dismiss after 3 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 3000);
            }
        }
    </script>
</body>
</html>