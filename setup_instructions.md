# Volt3dge PHP/MySQL Setup Instructions for DirectAdmin

## Prerequisites
- DirectAdmin hosting account
- PHP 7.4 or higher
- MySQL 5.7 or higher
- File Manager or FTP access

## Step 1: Database Setup

1. **Login to DirectAdmin**
   - Go to your DirectAdmin control panel
   - Navigate to "MySQL Management"

2. **Create Database**
   - Click "Create new Database"
   - Database name: `volt3dge_db` (or your preferred name)
   - Create a database user with full privileges
   - Note down the database credentials

3. **Import Database Schema**
   - Go to phpMyAdmin (usually available in DirectAdmin)
   - Select your database
   - Go to "Import" tab
   - Upload the `database/schema.sql` file
   - Click "Go" to execute

## Step 2: File Upload

1. **Upload Files**
   - Use File Manager or FTP client
   - Upload all PHP files to your domain's public_html directory
   - Maintain the folder structure

2. **Set Permissions**
   - Set `uploads/` folder to 755 or 777 permissions
   - Set `config/` folder to 755 permissions
   - Ensure PHP files have 644 permissions

## Step 3: Configuration

1. **Database Configuration**
   - Edit `config/database.php`
   - Update database credentials:
     ```php
     private $host = 'localhost';
     private $db_name = 'your_database_name';
     private $username = 'your_db_username';
     private $password = 'your_db_password';
     ```

2. **Site Configuration**
   - Edit `config/config.php`
   - Update `SITE_URL` to your domain:
     ```php
     define('SITE_URL', 'https://yourdomain.com');
     ```

3. **Create Upload Directories**
   - Create `uploads/` folder in root
   - Create `uploads/stl_files/` subfolder
   - Create `uploads/products/` subfolder
   - Set appropriate permissions (755 or 777)

## Step 4: Security Setup

1. **SSL Certificate**
   - Enable SSL in DirectAdmin
   - Update `config/config.php`:
     ```php
     ini_set('session.cookie_secure', 1); // Set to 1 for HTTPS
     ```

2. **File Permissions**
   - Ensure sensitive files are not publicly accessible
   - The `.htaccess` file provides additional security

## Step 5: Testing

1. **Access Your Site**
   - Visit your domain
   - Test user registration and login
   - Test product browsing
   - Test STL file upload

2. **Admin Access**
   - Login with admin credentials:
     - Username: `admin`
     - Password: `admin123`
   - Change admin password immediately
   - Access admin panel at: `yourdomain.com/admin/`

## Step 6: Customization

1. **Add Products**
   - Login to admin panel
   - Add product categories
   - Upload product images to `uploads/products/`
   - Add products with images

2. **Customize Design**
   - Modify CSS in `includes/header.php`
   - Update colors, fonts, and layout as needed
   - Add your logo and branding

## Important Security Notes

1. **Change Default Passwords**
   - Change admin password immediately
   - Use strong passwords for database

2. **Regular Updates**
   - Keep PHP and MySQL updated
   - Monitor for security vulnerabilities

3. **Backup Strategy**
   - Regular database backups
   - File system backups
   - Test restore procedures

## Troubleshooting

### Common Issues:

1. **Database Connection Error**
   - Check database credentials in `config/database.php`
   - Ensure database exists and user has privileges

2. **File Upload Issues**
   - Check folder permissions (755 or 777)
   - Verify PHP upload limits in DirectAdmin

3. **Session Issues**
   - Ensure session directory is writable
   - Check PHP session configuration

4. **Image Display Issues**
   - Verify image paths in database
   - Check file permissions
   - Ensure images are in correct directory

### Performance Optimization:

1. **Enable Caching**
   - Use `.htaccess` for browser caching
   - Consider implementing PHP caching

2. **Database Optimization**
   - Add indexes for frequently queried columns
   - Regular database maintenance

3. **Image Optimization**
   - Compress images before upload
   - Use appropriate image formats

## Support

For technical support or customization:
- Check DirectAdmin documentation
- Contact your hosting provider for server-specific issues
- Review PHP error logs for debugging

## Features Included

- ✅ User registration and authentication
- ✅ Product catalog with categories
- ✅ Shopping cart functionality
- ✅ Order management
- ✅ STL file upload and management
- ✅ Admin panel with black theme
- ✅ Mobile-responsive design
- ✅ Security measures (CSRF protection, SQL injection prevention)
- ✅ Analytics and reporting
- ✅ Modern dark theme design

## Removed Features

- ❌ Google Sheets integration (removed as requested)
- ❌ OrcaSlicer integration (simplified for basic hosting)
- ❌ Docker configuration (not needed for DirectAdmin)
- ❌ PostgreSQL (converted to MySQL)
- ❌ Django-specific features

The website is now fully compatible with DirectAdmin hosting and uses standard PHP/MySQL stack.