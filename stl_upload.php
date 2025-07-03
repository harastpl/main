<?php
require_once 'config/config.php';
require_once 'config/database.php';
require_once 'classes/STLFile.php';

$page_title = 'Upload STL File';

$error_message = '';
$success_message = '';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (!verify_csrf_token($_POST['csrf_token'])) {
        $error_message = 'Invalid security token.';
    } else {
        $name = sanitize_input($_POST['name']);
        $description = sanitize_input($_POST['description']);
        $print_quality = sanitize_input($_POST['print_quality']);
        $infill_percentage = (int)$_POST['infill_percentage'];
        $supports_needed = isset($_POST['supports_needed']) ? 1 : 0;

        if (empty($name)) {
            $error_message = 'Please enter a name for your STL file.';
        } elseif (!isset($_FILES['stl_file']) || $_FILES['stl_file']['error'] !== UPLOAD_ERR_OK) {
            $error_message = 'Please select a valid STL file.';
        } else {
            $database = new Database();
            $db = $database->getConnection();
            $stl_file = new STLFile($db);

            $user_id = is_logged_in() ? $_SESSION['user_id'] : null;
            $session_id = session_id();

            $file_id = $stl_file->upload($user_id, $session_id, $name, $description, $_FILES['stl_file'], 
                                       $print_quality, $infill_percentage, $supports_needed);

            if ($file_id) {
                $_SESSION['success_message'] = 'STL file uploaded successfully! Processing will begin shortly.';
                header('Location: stl_detail.php?id=' . $file_id);
                exit();
            } else {
                $error_message = 'Failed to upload STL file. Please check file format and size.';
            }
        }
    }
}

include 'includes/header.php';
?>

<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h4><i class="fas fa-upload"></i> Upload Your STL File</h4>
                    <p class="mb-0 text-muted">Upload your 3D model for custom printing</p>
                </div>
                <div class="card-body">
                    <!-- Upload Instructions -->
                    <div class="alert alert-info">
                        <h6><i class="fas fa-info-circle"></i> Upload Guidelines:</h6>
                        <ul class="mb-0">
                            <li>Only STL files are accepted</li>
                            <li>Maximum file size: 50MB</li>
                            <li>Your file will be processed automatically</li>
                            <li>Processing may take a few minutes</li>
                        </ul>
                    </div>

                    <?php if ($error_message): ?>
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> <?php echo $error_message; ?>
                        </div>
                    <?php endif; ?>

                    <form method="post" enctype="multipart/form-data" id="stl-upload-form">
                        <input type="hidden" name="csrf_token" value="<?php echo generate_csrf_token(); ?>">
                        
                        <div class="mb-3">
                            <label for="name" class="form-label">Model Name *</label>
                            <input type="text" class="form-control" id="name" name="name" 
                                   value="<?php echo isset($_POST['name']) ? htmlspecialchars($_POST['name']) : ''; ?>" 
                                   placeholder="Enter a name for your model" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="description" class="form-label">Description</label>
                            <textarea class="form-control" id="description" name="description" rows="3" 
                                      placeholder="Describe your model (optional)"><?php echo isset($_POST['description']) ? htmlspecialchars($_POST['description']) : ''; ?></textarea>
                        </div>
                        
                        <div class="mb-3">
                            <label for="stl_file" class="form-label">STL File *</label>
                            <input type="file" class="form-control" id="stl_file" name="stl_file" accept=".stl" required>
                            <div class="form-text">Select your STL file (max 50MB)</div>
                            <div id="file-info" class="mt-2" style="display: none;">
                                <small class="text-muted">
                                    <i class="fas fa-file"></i> 
                                    <span id="file-name"></span> 
                                    (<span id="file-size"></span>)
                                </small>
                            </div>
                        </div>

                        <h6 class="mt-4 mb-3">Print Settings</h6>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="print_quality" class="form-label">Print Quality</label>
                                <select class="form-select" id="print_quality" name="print_quality">
                                    <option value="draft">Draft (0.3mm)</option>
                                    <option value="normal" selected>Normal (0.2mm)</option>
                                    <option value="fine">Fine (0.15mm)</option>
                                    <option value="ultra_fine">Ultra Fine (0.1mm)</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="infill_percentage" class="form-label">Infill Percentage</label>
                                <select class="form-select" id="infill_percentage" name="infill_percentage">
                                    <option value="10">10%</option>
                                    <option value="15">15%</option>
                                    <option value="20" selected>20%</option>
                                    <option value="25">25%</option>
                                    <option value="50">50%</option>
                                    <option value="75">75%</option>
                                    <option value="100">100%</option>
                                </select>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="supports_needed" name="supports_needed">
                                <label class="form-check-label" for="supports_needed">
                                    Add support structures (recommended for overhangs)
                                </label>
                            </div>
                        </div>

                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="my_stl_files.php" class="btn btn-outline-secondary me-md-2">
                                <i class="fas fa-arrow-left"></i> Back to Files
                            </a>
                            <button type="submit" class="btn btn-primary" id="upload-btn">
                                <i class="fas fa-upload"></i> Upload & Process
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- Processing Info -->
            <div class="card mt-4">
                <div class="card-body">
                    <h6><i class="fas fa-cogs"></i> What happens after upload?</h6>
                    <div class="row">
                        <div class="col-md-3 text-center">
                            <i class="fas fa-upload fa-2x text-primary mb-2"></i>
                            <h6>1. Upload</h6>
                            <small class="text-muted">Your STL file is uploaded securely</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <i class="fas fa-cog fa-2x text-warning mb-2"></i>
                            <h6>2. Process</h6>
                            <small class="text-muted">System analyzes your model</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <i class="fas fa-eye fa-2x text-info mb-2"></i>
                            <h6>3. Preview</h6>
                            <small class="text-muted">Generate preview and estimates</small>
                        </div>
                        <div class="col-md-3 text-center">
                            <i class="fas fa-print fa-2x text-success mb-2"></i>
                            <h6>4. Print</h6>
                            <small class="text-muted">Ready for 3D printing</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('stl_file');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const uploadBtn = document.getElementById('upload-btn');
    const form = document.getElementById('stl-upload-form');

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';
            
            // Validate file
            if (!file.name.toLowerCase().endsWith('.stl')) {
                showMessage('Please select an STL file.', 'danger');
                fileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }
            
            if (file.size > 50 * 1024 * 1024) {
                showMessage('File size cannot exceed 50MB.', 'danger');
                fileInput.value = '';
                fileInfo.style.display = 'none';
                return;
            }
        } else {
            fileInfo.style.display = 'none';
        }
    });

    form.addEventListener('submit', function(e) {
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
        uploadBtn.disabled = true;
    });

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});
</script>

<?php include 'includes/footer.php'; ?>