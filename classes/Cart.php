<?php
require_once 'config/database.php';

class Cart {
    private $conn;
    private $table_name = "cart";

    public function __construct($db) {
        $this->conn = $db;
    }

    public function getOrCreateCart($user_id = null, $session_id = null) {
        if ($user_id) {
            $query = "SELECT id FROM " . $this->table_name . " WHERE user_id = :user_id";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':user_id', $user_id);
        } else {
            $query = "SELECT id FROM " . $this->table_name . " WHERE session_id = :session_id";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':session_id', $session_id);
        }
        
        $stmt->execute();
        $cart = $stmt->fetch();
        
        if (!$cart) {
            // Create new cart
            $query = "INSERT INTO " . $this->table_name . " (user_id, session_id) VALUES (:user_id, :session_id)";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':user_id', $user_id);
            $stmt->bindParam(':session_id', $session_id);
            $stmt->execute();
            return $this->conn->lastInsertId();
        }
        
        return $cart['id'];
    }

    public function addItem($cart_id, $product_id, $quantity = 1) {
        // Check if item already exists
        $query = "SELECT id, quantity FROM cart_items WHERE cart_id = :cart_id AND product_id = :product_id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':cart_id', $cart_id);
        $stmt->bindParam(':product_id', $product_id);
        $stmt->execute();
        
        $existing_item = $stmt->fetch();
        
        if ($existing_item) {
            // Update quantity
            $new_quantity = $existing_item['quantity'] + $quantity;
            $query = "UPDATE cart_items SET quantity = :quantity WHERE id = :id";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':quantity', $new_quantity);
            $stmt->bindParam(':id', $existing_item['id']);
            return $stmt->execute();
        } else {
            // Add new item
            $query = "INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (:cart_id, :product_id, :quantity)";
            $stmt = $this->conn->prepare($query);
            $stmt->bindParam(':cart_id', $cart_id);
            $stmt->bindParam(':product_id', $product_id);
            $stmt->bindParam(':quantity', $quantity);
            return $stmt->execute();
        }
    }

    public function getItems($cart_id) {
        $query = "SELECT ci.*, p.name, p.price, p.image, p.stock 
                  FROM cart_items ci 
                  JOIN products p ON ci.product_id = p.id 
                  WHERE ci.cart_id = :cart_id";
        
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':cart_id', $cart_id);
        $stmt->execute();
        
        return $stmt->fetchAll();
    }

    public function updateQuantity($item_id, $quantity) {
        if ($quantity <= 0) {
            return $this->removeItem($item_id);
        }
        
        $query = "UPDATE cart_items SET quantity = :quantity WHERE id = :id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':quantity', $quantity);
        $stmt->bindParam(':id', $item_id);
        return $stmt->execute();
    }

    public function removeItem($item_id) {
        $query = "DELETE FROM cart_items WHERE id = :id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':id', $item_id);
        return $stmt->execute();
    }

    public function clearCart($cart_id) {
        $query = "DELETE FROM cart_items WHERE cart_id = :cart_id";
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':cart_id', $cart_id);
        return $stmt->execute();
    }

    public function getCartTotal($cart_id) {
        $query = "SELECT SUM(ci.quantity * p.price) as total, SUM(ci.quantity) as items 
                  FROM cart_items ci 
                  JOIN products p ON ci.product_id = p.id 
                  WHERE ci.cart_id = :cart_id";
        
        $stmt = $this->conn->prepare($query);
        $stmt->bindParam(':cart_id', $cart_id);
        $stmt->execute();
        
        return $stmt->fetch();
    }
}
?>