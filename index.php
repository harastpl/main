<?php
require_once 'config/config.php';
require_once 'config/database.php';
require_once 'classes/Product.php';

$page_title = 'Home';

$database = new Database();
$db = $database->getConnection();
$product = new Product($db);

// Get featured products
$featured_products = $product->getAll(8);

include 'includes/header.php';
?>

<!-- Hero Section -->
<div class="hero-section">
    <div class="container text-center">
        <h1 class="display-4 mb-3">Premium 3D Printing Services</h1>
        <p class="lead">Transform your ideas into reality with cutting-edge 3D printing technology</p>
        <div class="mt-4">
            <a href="products.php" class="btn btn-primary btn-lg me-3">
                <i class="fas fa-shopping-bag"></i> Browse Products
            </a>
            <a href="stl_upload.php" class="btn btn-outline-light btn-lg">
                <i class="fas fa-upload"></i> Upload STL
            </a>
        </div>
    </div>
</div>

<div class="container">
    <!-- Features Section -->
    <div class="row mb-5">
        <div class="col-md-4 text-center mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <i class="fas fa-cube fa-3x text-primary mb-3"></i>
                    <h5>Custom 3D Printing</h5>
                    <p>Upload your STL files and get professional 3D prints with various materials and finishes.</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 text-center mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <i class="fas fa-rocket fa-3x text-primary mb-3"></i>
                    <h5>Fast Delivery</h5>
                    <p>Quick turnaround times with reliable shipping to get your prints when you need them.</p>
                </div>
            </div>
        </div>
        <div class="col-md-4 text-center mb-4">
            <div class="card h-100">
                <div class="card-body">
                    <i class="fas fa-award fa-3x text-primary mb-3"></i>
                    <h5>Premium Quality</h5>
                    <p>High-quality prints using professional-grade 3D printers and premium materials.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Featured Products -->
    <h2 class="text-center mb-4">Featured Products</h2>
    <div class="row">
        <?php foreach ($featured_products as $prod): ?>
            <div class="col-lg-3 col-md-4 col-sm-6 mb-4">
                <div class="card h-100">
                    <div class="position-relative overflow-hidden">
                        <img src="<?php echo $prod['image'] ? 'uploads/products/' . $prod['image'] : 'https://via.placeholder.com/300x250?text=No+Image'; ?>" 
                             class="card-img-top product-image" alt="<?php echo htmlspecialchars($prod['name']); ?>">
                        <?php if ($prod['stock'] <= 10 && $prod['stock'] > 0): ?>
                            <span class="badge bg-warning position-absolute top-0 end-0 m-2">Low Stock</span>
                        <?php elseif ($prod['stock'] == 0): ?>
                            <span class="badge bg-danger position-absolute top-0 end-0 m-2">Out of Stock</span>
                        <?php endif; ?>
                    </div>
                    
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title">
                            <a href="product_detail.php?id=<?php echo $prod['id']; ?>" class="text-decoration-none text-light">
                                <?php echo htmlspecialchars($prod['name']); ?>
                            </a>
                        </h5>
                        <p class="card-text text-muted small flex-grow-1">
                            <?php echo htmlspecialchars(substr($prod['description'], 0, 100)) . '...'; ?>
                        </p>
                        <div class="mt-auto">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="h5 text-primary">₹<?php echo number_format($prod['price'], 2); ?></span>
                            </div>
                            <div class="d-grid gap-2">
                                <a href="product_detail.php?id=<?php echo $prod['id']; ?>" 
                                   class="btn btn-outline-primary btn-sm">
                                    <i class="fas fa-info-circle"></i> View Details
                                </a>
                                <?php if ($prod['stock'] > 0): ?>
                                    <button onclick="addToCart(<?php echo $prod['id']; ?>)" class="btn btn-primary btn-sm">
                                        <i class="fas fa-cart-plus"></i> Add to Cart
                                    </button>
                                    <input type="hidden" name="csrf_token" value="<?php echo generate_csrf_token(); ?>">
                                <?php else: ?>
                                    <button class="btn btn-secondary btn-sm" disabled>
                                        <i class="fas fa-times"></i> Out of Stock
                                    </button>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        <?php endforeach; ?>
    </div>

    <div class="text-center mt-4">
        <a href="products.php" class="btn btn-primary btn-lg">
            <i class="fas fa-arrow-right"></i> View All Products
        </a>
    </div>
</div>

<?php include 'includes/footer.php'; ?>