import React, { useState } from 'react';

const Shopping = ({ vehicleData }) => {
  const [cart, setCart] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [showCart, setShowCart] = useState(false);

  const categories = ['All', 'Maintenance', 'Tires', 'Safety', 'Accessories'];

  const [products] = useState([
    { 
      id: 1, 
      name: 'Mobil 1 Synthetic Oil', 
      price: 29.99, 
      category: 'Maintenance', 
      rating: 4.8, 
      image: '🛢️',
      description: 'Premium full synthetic motor oil',
      discount: 15,
      recommended: true
    },
    { 
      id: 2, 
      name: 'Michelin Premier Tires', 
      price: 145.00, 
      category: 'Tires', 
      rating: 4.9, 
      image: '🛞',
      description: 'All-season premium tires',
      discount: 20,
      recommended: true
    },
    { 
      id: 3, 
      name: 'Emergency Roadside Kit', 
      price: 49.99, 
      category: 'Safety', 
      rating: 4.7, 
      image: '🚨',
      description: 'Complete emergency kit with tools',
      discount: 25,
      recommended: true
    },
    { 
      id: 4, 
      name: 'Wireless Phone Mount', 
      price: 24.99, 
      category: 'Accessories', 
      rating: 4.6, 
      image: '📱',
      description: 'Qi wireless charging mount',
      discount: 30,
      recommended: false
    },
    { 
      id: 5, 
      name: 'K&N Air Filter', 
      price: 45.99, 
      category: 'Maintenance', 
      rating: 4.7, 
      image: '🔧',
      description: 'High-flow performance air filter',
      discount: 10,
      recommended: false
    },
    { 
      id: 6, 
      name: 'USB-C Car Charger', 
      price: 19.99, 
      category: 'Accessories', 
      rating: 4.4, 
      image: '🔌',
      description: 'Fast charging dual port charger',
      discount: 0,
      recommended: false
    }
  ]);

  const filteredProducts = products.filter(product => {
    return selectedCategory === 'All' || product.category === selectedCategory;
  });

  const addToCart = (product) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.id === product.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevCart, { ...product, quantity: 1 }];
      }
    });
  };

  const updateQuantity = (id, newQuantity) => {
    if (newQuantity === 0) {
      setCart(prevCart => prevCart.filter(item => item.id !== id));
    } else {
      setCart(prevCart =>
        prevCart.map(item =>
          item.id === id ? { ...item, quantity: newQuantity } : item
        )
      );
    }
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => {
      const discountedPrice = item.price * (1 - (item.discount || 0) / 100);
      return total + (discountedPrice * item.quantity);
    }, 0);
  };

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  const checkout = () => {
    const orderTotal = getTotalPrice();
    const tax = orderTotal * 0.08;
    const shipping = orderTotal > 75 ? 0 : 9.99;
    const finalTotal = orderTotal + tax + shipping;
    
    alert(`🎉 Order placed successfully!\n\nSubtotal: $${orderTotal.toFixed(2)}\nTax: $${tax.toFixed(2)}\nShipping: $${shipping.toFixed(2)}\nTotal: $${finalTotal.toFixed(2)}\n\nEstimated delivery: 3-5 business days`);
    setCart([]);
    setShowCart(false);
  };

  if (!vehicleData) {
    return <div className="loading">Loading products...</div>;
  }

  return (
    <div className="animate-slide-up">
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '5px', color: '#fff' }}>
            Vehicle Shop
          </h1>
          <p style={{ color: '#888', fontSize: '14px' }}>
            Personalized for your {vehicleData.vehicle.make} {vehicleData.vehicle.model}
          </p>
        </div>
        <div 
          style={{ position: 'relative', cursor: 'pointer' }}
          onClick={() => setShowCart(!showCart)}
        >
          <span style={{ fontSize: '24px' }}>🛒</span>
          {getTotalItems() > 0 && (
            <span style={{
              position: 'absolute',
              top: '-8px',
              right: '-8px',
              background: '#ff4757',
              color: '#fff',
              borderRadius: '50%',
              width: '20px',
              height: '20px',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: '600'
            }}>
              {getTotalItems()}
            </span>
          )}
        </div>
      </div>

      {/* AI Recommendations Banner */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '16px',
        padding: '20px',
        marginBottom: '20px',
        border: '1px solid rgba(255, 255, 255, 0.1)'
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px', color: '#fff' }}>
          🤖 AI Recommendations
        </h3>
        <p style={{ fontSize: '14px', color: '#fff', opacity: 0.9, marginBottom: '10px' }}>
          Based on your vehicle health and driving patterns:
        </p>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {products.filter(p => p.recommended).map(product => (
            <span key={product.id} style={{
              background: 'rgba(255, 255, 255, 0.2)',
              padding: '4px 8px',
              borderRadius: '12px',
              fontSize: '12px',
              fontWeight: '500',
              color: '#fff'
            }}>
              {product.name}
            </span>
          ))}
        </div>
      </div>

      {/* Category Filter */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '5px' }}>
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              style={{
                background: selectedCategory === category ? '#00ff88' : 'rgba(255, 255, 255, 0.1)',
                color: selectedCategory === category ? '#000' : '#fff',
                border: 'none',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '500',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.3s ease'
              }}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      <div className="product-grid" style={{ marginBottom: showCart ? '300px' : '100px' }}>
        {filteredProducts.map(product => (
          <div key={product.id} className="product-card">
            <div style={{ position: 'relative' }}>
              {product.recommended && (
                <span style={{
                  position: 'absolute',
                  top: '5px',
                  right: '5px',
                  background: '#00ff88',
                  color: '#000',
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '8px',
                  fontWeight: '600'
                }}>
                  AI Pick
                </span>
              )}
              {product.discount > 0 && (
                <span style={{
                  position: 'absolute',
                  top: '5px',
                  left: '5px',
                  background: '#ff4757',
                  color: '#fff',
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '8px',
                  fontWeight: '600'
                }}>
                  -{product.discount}%
                </span>
              )}
              <div className="product-image" style={{ fontSize: '24px' }}>{product.image}</div>
            </div>
            
            <div className="product-name">{product.name}</div>
            <p style={{ fontSize: '11px', color: '#888', marginBottom: '8px' }}>
              {product.description}
            </p>
            
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px' }}>⭐</span>
              <span style={{ fontSize: '12px', color: '#888', marginLeft: '4px' }}>
                {product.rating}
              </span>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                {product.discount > 0 ? (
                  <div>
                    <span style={{ 
                      fontSize: '12px', 
                      color: '#888', 
                      textDecoration: 'line-through' 
                    }}>
                      ${product.price}
                    </span>
                    <div className="product-price">
                      ${(product.price * (1 - product.discount / 100)).toFixed(2)}
                    </div>
                  </div>
                ) : (
                  <div className="product-price">${product.price}</div>
                )}
              </div>
              
              <button
                onClick={() => addToCart(product)}
                style={{
                  background: '#00ff88',
                  color: '#000',
                  border: 'none',
                  borderRadius: '8px',
                  width: '28px',
                  height: '28px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  fontWeight: '600',
                  fontSize: '16px'
                }}
              >
                +
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Shopping Cart Overlay */}
      {showCart && (
        <div style={{
          position: 'fixed',
          bottom: '90px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '355px',
          maxHeight: '400px',
          background: 'rgba(0, 0, 0, 0.95)',
          borderRadius: '20px',
          padding: '20px',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          zIndex: 1000
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#fff' }}>Shopping Cart</h3>
            <button 
              onClick={() => setShowCart(false)}
              style={{ background: 'none', border: 'none', color: '#888', fontSize: '18px', cursor: 'pointer' }}
            >
              ✕
            </button>
          </div>

          {cart.length === 0 ? (
            <p style={{ color: '#888', textAlign: 'center', padding: '20px' }}>
              Your cart is empty
            </p>
          ) : (
            <>
              <div style={{ maxHeight: '200px', overflowY: 'auto', marginBottom: '15px' }}>
                {cart.map(item => (
                  <div key={item.id} className="cart-item">
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '14px', fontWeight: '500', marginBottom: '5px', color: '#fff' }}>
                        {item.name}
                      </div>
                      <div style={{ fontSize: '14px', color: '#00ff88' }}>
                        ${(item.price * (1 - (item.discount || 0) / 100)).toFixed(2)}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        style={{
                          background: 'rgba(255, 255, 255, 0.1)',
                          border: 'none',
                          color: '#fff',
                          width: '24px',
                          height: '24px',
                          borderRadius: '6px',
                          cursor: 'pointer'
                        }}
                      >
                        -
                      </button>
                      <span style={{ fontSize: '14px', minWidth: '20px', textAlign: 'center', color: '#fff' }}>
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        style={{
                          background: 'rgba(255, 255, 255, 0.1)',
                          border: 'none',
                          color: '#fff',
                          width: '24px',
                          height: '24px',
                          borderRadius: '6px',
                          cursor: 'pointer'
                        }}
                      >
                        +
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="cart-total" style={{ marginBottom: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                  <span>Subtotal:</span>
                  <span>${getTotalPrice().toFixed(2)}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', opacity: 0.8 }}>
                  <span>+ Tax & Shipping</span>
                  <span>{getTotalPrice() > 75 ? 'Free shipping!' : '+$9.99'}</span>
                </div>
              </div>

              <button 
                className="btn" 
                onClick={checkout}
                style={{ 
                  width: '100%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                💳 Checkout ({getTotalItems()} items)
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Shopping;
