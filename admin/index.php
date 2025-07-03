<?php
require_once '../config/config.php';
require_once '../config/database.php';

require_admin();

$page_title = 'Admin Dashboard';

$database = new Database();
$db = $database->getConnection();

// Get statistics
$stats = array();

// Total users
$query = "SELECT COUNT(*) as total FROM users WHERE is_admin = 0";
$stmt = $db->prepare($query);
$stmt->execute();
$stats['users'] = $stmt->fetch()['total'];

// Total products
$query = "SELECT COUNT(*) as total FROM products";
$stmt = $db->prepare($query);
$stmt->execute();
$stats['products'] = $stmt->fetch()['total'];

// Total orders
$query = "SELECT COUNT(*) as total FROM orders";
$stmt = $db->prepare($query);
$stmt->execute();
$stats['orders'] = $stmt->fetch()['total'];

// Total STL files
$query = "SELECT COUNT(*) as total FROM stl_files";
$stmt = $db->prepare($query);
$stmt->execute();
$stats['stl_files'] = $stmt->fetch()['total'];

// Recent orders
$query = "SELECT o.*, u.username FROM orders o 
          LEFT JOIN users u ON o.user_id = u.id 
          ORDER BY o.created_at DESC LIMIT 10";
$stmt = $db->prepare($query);
$stmt->execute();
$recent_orders = $stmt->fetchAll();

// Recent STL uploads
$query = "SELECT s.*, u.username FROM stl_files s 
          LEFT JOIN users u ON s.user_id = u.id 
          ORDER BY s.created_at DESC LIMIT 10";
$stmt = $db->prepare($query);
$stmt->execute();
$recent_stl_files = $stmt->fetchAll();

include 'includes/admin_header.php';
?>

<div class="container-fluid mt-4">
    <h2>Dashboard Overview</h2>
    
    <!-- Statistics Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4><?php echo $stats['users']; ?></h4>
                            <p>Total Users</p>
                        </div>
                        <div>
                            <i class="fas fa-users fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4><?php echo $stats['products']; ?></h4>
                            <p>Total Products</p>
                        </div>
                        <div>
                            <i class="fas fa-box fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-warning text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4><?php echo $stats['orders']; ?></h4>
                            <p>Total Orders</p>
                        </div>
                        <div>
                            <i class="fas fa-shopping-cart fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-info text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <div>
                            <h4><?php echo $stats['stl_files']; ?></h4>
                            <p>STL Files</p>
                        </div>
                        <div>
                            <i class="fas fa-cube fa-2x"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <!-- Recent Orders -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Orders</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Order ID</th>
                                    <th>Customer</th>
                                    <th>Total</th>
                                    <th>Status</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($recent_orders as $order): ?>
                                    <tr>
                                        <td>#<?php echo $order['id']; ?></td>
                                        <td><?php echo $order['username'] ?: $order['first_name'] . ' ' . $order['last_name']; ?></td>
                                        <td>₹<?php echo number_format($order['total'], 2); ?></td>
                                        <td>
                                            <span class="badge bg-<?php echo $order['status'] == 'pending' ? 'warning' : 'success'; ?>">
                                                <?php echo ucfirst($order['status']); ?>
                                            </span>
                                        </td>
                                        <td><?php echo date('M d', strtotime($order['created_at'])); ?></td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent STL Files -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Recent STL Uploads</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>File Name</th>
                                    <th>User</th>
                                    <th>Status</th>
                                    <th>Size</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                <?php foreach ($recent_stl_files as $file): ?>
                                    <tr>
                                        <td><?php echo htmlspecialchars($file['name']); ?></td>
                                        <td><?php echo $file['username'] ?: 'Anonymous'; ?></td>
                                        <td>
                                            <span class="badge bg-<?php 
                                                echo $file['status'] == 'processed' ? 'success' : 
                                                    ($file['status'] == 'processing' ? 'warning' : 'secondary'); 
                                            ?>">
                                                <?php echo ucfirst($file['status']); ?>
                                            </span>
                                        </td>
                                        <td><?php echo round($file['file_size'] / 1024 / 1024, 2); ?> MB</td>
                                        <td><?php echo date('M d', strtotime($file['created_at'])); ?></td>
                                    </tr>
                                <?php endforeach; ?>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<?php include 'includes/admin_footer.php'; ?>