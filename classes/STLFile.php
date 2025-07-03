<?php
require_once 'config/database.php';

class STLFile {
    private $conn;
    private $table_name = "stl_files";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function upload($user_id, $session_id, $name, $description, $file_info, $print_quality, $infill_percentage, $supports_needed) {
        // Validate file
        if ($file_info['error'] !== UPLOAD_ERR_OK) {
            return false;
        }

        $allowed_types = ['application/octet-stream', 'application/sla'];
        $file_extension = strtolower(pathinfo($file_info['name'], PATHINFO_EXTENSION));
        
        if ($file_extension !== 'stl') {
            return false;
        }

        if ($file_info['size'] > MAX_FILE_SIZE) {
            return false;
        }

        // Create upload directory
        $upload_dir = UPLOAD_PATH . 'stl_files/';
        if (!file_exists($upload_dir)) {
            mkdir($upload_dir, 0755, true);
        }

        // Generate unique filename
        $filename = uniqid() . '_' . time() . '.stl';
        $file_path = $upload_dir . $filename;

        // Move uploaded file
        if (!move_uploaded_file($file_info['tmp_name'], $file_path)) {
            return false;
        }

        // Insert into database
        $query = "INSERT INTO " . $this->table_name . " 
                  (user_id, session_id, name, description, file_path, file_size, print_quality, infill_percentage, supports_needed) 
                  VALUES (:user_id, :session_id, :name, :description, :file_path, :file_size, :print_quality, :infill_percentage, :supports_needed)";
        
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':user_id', $user_id);
        $stmt->bindParam(':session_id', $session_id);
        $stmt->bindParam(':name', $name);
        $stmt->bindParam(':description', $description);
        $stmt->bindParam(':file_path', $file_path);
        $stmt->bindParam(':file_size', $file_info['size']);
        $stmt->bindParam(':print_quality', $print_quality);
        $stmt->bindParam(':infill_percentage', $infill_percentage);
        $stmt->bindParam(':supports_needed', $supports_needed);

        if ($stmt->execute()) {
            return $this->conn->lastInsertId();
        }
        
        return false;
    }

    public function getUserFiles($user_id, $session_id = null, $limit = 12, $offset = 0, $search = null, $status = null) {
        $query = "SELECT * FROM " . $this->table_name . " WHERE ";
        $params = array();
        
        if ($user_id) {
            $query .= "user_id = :user_id";
            $params[':user_id'] = $user_id;
        } else {
            $query .= "session_id = :session_id";
            $params[':session_id'] = $session_id;
        }
        
        if ($search) {
            $query .= " AND (name LIKE :search OR description LIKE :search)";
            $params[':search'] = '%' . $search . '%';
        }
        
        if ($status) {
            $query .= " AND status = :status";
            $params[':status'] = $status;
        }
        
        $query .= " ORDER BY created_at DESC LIMIT :limit OFFSET :offset";
        
        $stmt = $this->conn->prepare($query);
        
        foreach ($params as $key => $value) {
            $stmt->bindValue($key, $value);
        }
        
        $stmt->bindValue(':limit', $limit, PDO::PARAM_INT);
        $stmt->bindValue(':offset', $offset, PDO::PARAM_INT);
        $stmt->execute();
        
        return $stmt->fetchAll();
    }

    public function getById($id) {
        $query = "SELECT * FROM " . $this->table_name . " WHERE id = :id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':id', $id);
        $stmt->execute();
        return $stmt->fetch();
    }

    public function updateStatus($id, $status, $estimated_cost = null, $estimated_time = null) {
        $query = "UPDATE " . $this->table_name . " SET status = :status";
        $params = array(':status' => $status, ':id' => $id);
        
        if ($estimated_cost !== null) {
            $query .= ", estimated_cost = :estimated_cost";
            $params[':estimated_cost'] = $estimated_cost;
        }
        
        if ($estimated_time !== null) {
            $query .= ", estimated_print_time = :estimated_time";
            $params[':estimated_time'] = $estimated_time;
        }
        
        $query .= " WHERE id = :id";
        
        $stmt = $this->conn->prepare($query);
        
        foreach ($params as $key => $value) {
            $stmt->bindValue($key, $value);
        }
        
        return $stmt->execute();
    }

    public function delete($id) {
        // Get file path first
        $file = $this->getById($id);
        if ($file && file_exists($file['file_path'])) {
            unlink($file['file_path']);
        }
        
        $query = "DELETE FROM " . $this->table_name . " WHERE id = :id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':id', $id);
        return $stmt->execute();
    }
}
?>