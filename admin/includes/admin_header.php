<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo isset($page_title) ? $page_title . ' - ' : ''; ?>Volt3dge Admin</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --admin-primary: #000000;
            --admin-secondary: #1a1a1a;
            --admin-accent: #ff6b35;
            --admin-text: #ffffff;
            --admin-muted: #cccccc;
        }

        body {
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            color: var(--admin-text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        .navbar {
            background: var(--admin-primary) !important;
            border-bottom: 2px solid var(--admin-accent);
        }

        .navbar-brand {
            color: var(--admin-accent) !important;
            font-weight: bold;
        }

        .navbar-nav .nav-link {
            color: var(--admin-text) !important;
        }

        .navbar-nav .nav-link:hover {
            color: var(--admin-accent) !important;
        }

        .sidebar {
            background: var(--admin-secondary);
            min-height: calc(100vh - 56px);
            border-right: 1px solid #333;
        }

        .sidebar .nav-link {
            color: var(--admin-muted);
            padding: 0.75rem 1rem;
            border-radius: 0;
        }

        .sidebar .nav-link:hover,
        .sidebar .nav-link.active {
            background: var(--admin-accent);
            color: white;
        }

        .card {
            background: var(--admin-secondary);
            border: 1px solid #333;
            color: var(--admin-text);
        }

        .table {
            color: var(--admin-text);
        }

        .table th {
            border-color: #333;
            background: var(--admin-primary);
        }

        .table td {
            border-color: #333;
        }

        .btn-primary {
            background: var(--admin-accent);
            border-color: var(--admin-accent);
        }

        .btn-primary:hover {
            background: #ff8c42;
            border-color: #ff8c42;
        }

        .form-control {
            background: #333;
            border-color: #555;
            color: var(--admin-text);
        }

        .form-control:focus {
            background: #333;
            border-color: var(--admin-accent);
            color: var(--admin-text);
            box-shadow: 0 0 0 0.2rem rgba(255, 107, 53, 0.25);
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a href="index.php" class="navbar-brand">
                <i class="fas fa-bolt"></i> Volt3dge Admin
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="../index.php" target="_blank">
                            <i class="fas fa-external-link-alt"></i> View Site
                        </a>
                    </li>
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" 
                           data-bs-toggle="dropdown">
                            <i class="fas fa-user"></i> <?php echo htmlspecialchars($_SESSION['username']); ?>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-dark">
                            <li><a class="dropdown-item" href="../logout.php">Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2 sidebar">
                <nav class="nav flex-column">
                    <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'index.php' ? 'active' : ''; ?>" 
                       href="index.php">
                        <i class="fas fa-tachometer-alt"></i> Dashboard
                    </a>
                    <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'products.php' ? 'active' : ''; ?>" 
                       href="products.php">
                        <i class="fas fa-box"></i> Products
                    </a>
                    <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'orders.php' ? 'active' : ''; ?>" 
                       href="orders.php">
                        <i class="fas fa-shopping-cart"></i> Orders
                    </a>
                    <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'stl_files.php' ? 'active' : ''; ?>" 
                       href="stl_files.php">
                        <i class="fas fa-cube"></i> STL Files
                    </a>
                    <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'users.php' ? 'active' : ''; ?>" 
                       href="users.php">
                        <i class="fas fa-users"></i> Users
                    </a>
                    <a class="nav-link <?php echo basename($_SERVER['PHP_SELF']) == 'analytics.php' ? 'active' : ''; ?>" 
                       href="analytics.php">
                        <i class="fas fa-chart-bar"></i> Analytics
                    </a>
                </nav>
            </div>

            <!-- Main Content -->
            <div class="col-md-10">