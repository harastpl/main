<?php
class Database {
    // DirectAdmin typically uses this format: username_databasename
    private $host = 'localhost';
    private $db_name = 'voltdgec_volt3dge'; // Change this to match DirectAdmin format
    private $username = 'voltdgec_admin';   // Your DirectAdmin MySQL username
    private $password = 'your_password';    // Your DirectAdmin MySQL password
    private $conn;

    public function getConnection() {
        $this->conn = null;
        try {
            $this->conn = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->db_name . ";charset=utf8",
                $this->username,
                $this->password,
                array(
                    PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                    PDO::ATTR_EMULATE_PREPARES => false
                )
            );
        } catch(PDOException $exception) {
            echo "Connection error: " . $exception->getMessage();
        }
        return $this->conn;
    }
}
?>