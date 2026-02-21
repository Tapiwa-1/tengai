const path = require('path');
const express = require('express');
const sqlite3 = require('sqlite3').verbose();

const app = express();
const PORT = process.env.PORT || 3000;
const DB_PATH = path.join(__dirname, 'store.db');

const db = new sqlite3.Database(DB_PATH);

app.use(express.json());
const CLIENT_DIST_PATH = path.join(__dirname, 'frontend', 'dist');

app.use(express.static(CLIENT_DIST_PATH));

const run = (sql, params = []) =>
  new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(err) {
      if (err) {
        reject(err);
        return;
      }
      resolve(this);
    });
  });

const all = (sql, params = []) =>
  new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(rows);
    });
  });

const get = (sql, params = []) =>
  new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
      if (err) {
        reject(err);
        return;
      }
      resolve(row);
    });
  });

async function initDb() {
  await run(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      category TEXT NOT NULL,
      price REAL NOT NULL,
      rating REAL NOT NULL,
      image TEXT NOT NULL,
      badge TEXT,
      description TEXT NOT NULL
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS cart_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL DEFAULT 1,
      FOREIGN KEY (product_id) REFERENCES products (id)
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS coupons (
      code TEXT PRIMARY KEY,
      discount_percent REAL NOT NULL,
      min_subtotal REAL NOT NULL DEFAULT 0
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      subtotal REAL NOT NULL,
      discount REAL NOT NULL,
      total REAL NOT NULL,
      coupon_code TEXT,
      created_at TEXT NOT NULL
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS order_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      price REAL NOT NULL,
      FOREIGN KEY (order_id) REFERENCES orders (id),
      FOREIGN KEY (product_id) REFERENCES products (id)
    )
  `);

  const row = await get('SELECT COUNT(*) AS count FROM products');

  if (row.count === 0) {
    const seedProducts = [
      ['Echo Sphere Smart Speaker', 'Electronics', 79.99, 4.6, 'https://images.unsplash.com/photo-1589003077984-894e133dabab?auto=format&fit=crop&w=700&q=80', 'Limited time deal', 'Voice assistant smart speaker with room-filling sound and smart home controls.'],
      ['Nimbus Noise-Canceling Headphones', 'Electronics', 129.95, 4.4, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=700&q=80', 'Amazon Choice', 'Wireless over-ear headphones with active noise cancellation and 40-hour battery.'],
      ['KindLeaf Bamboo Sheet Set', 'Home', 49.99, 4.3, 'https://images.unsplash.com/photo-1616627455254-f67f2f2edaf6?auto=format&fit=crop&w=700&q=80', 'Best Seller', 'Soft breathable bamboo sheets with deep pockets for queen-sized mattresses.'],
      ['SwiftBrew Coffee Maker Pro', 'Kitchen', 89.0, 4.5, 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=700&q=80', null, 'Programmable 12-cup coffee machine with thermal carafe and auto-clean function.'],
      ['TrailFlex Running Shoes', 'Fashion', 64.5, 4.2, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=700&q=80', 'Prime', 'Lightweight running shoes designed for comfort and everyday performance.'],
      ['Luma 4K Streaming Stick', 'Electronics', 39.99, 4.7, 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?auto=format&fit=crop&w=700&q=80', 'Top Rated', 'Compact streaming device with ultra-HD playback and voice remote support.'],
      ['ChefMate 14pc Nonstick Set', 'Kitchen', 119.99, 4.1, 'https://images.unsplash.com/photo-1584990347449-a5d9f5a5f4ee?auto=format&fit=crop&w=700&q=80', null, 'Durable cookware set with induction-ready base and tempered glass lids.'],
      ['GlowDesk LED Monitor Lamp', 'Office', 34.99, 4.4, 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=700&q=80', 'Deal of the day', 'Eye-care desk lamp with touch controls, dimming, and USB-C charging port.']
    ];

    for (const product of seedProducts) {
      await run(
        `INSERT INTO products (title, category, price, rating, image, badge, description)
         VALUES (?, ?, ?, ?, ?, ?, ?)`,
        product
      );
    }
  }

  const couponCount = await get('SELECT COUNT(*) AS count FROM coupons');

  if (couponCount.count === 0) {
    const seedCoupons = [
      ['SAVE10', 10, 50],
      ['PRIME20', 20, 120],
      ['WELCOME5', 5, 0]
    ];

    for (const coupon of seedCoupons) {
      await run('INSERT INTO coupons (code, discount_percent, min_subtotal) VALUES (?, ?, ?)', coupon);
    }
  }
}

function calculateCartTotals(items, discountPercent = 0) {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const discount = subtotal * (discountPercent / 100);
  const total = Math.max(subtotal - discount, 0);

  return {
    subtotal,
    discount,
    total
  };
}

app.get('/api/products', async (req, res) => {
  const { q = '', category = '', sort = '' } = req.query;

  try {
    let query = 'SELECT * FROM products WHERE 1=1';
    const params = [];

    if (q.trim()) {
      query += ' AND (title LIKE ? OR description LIKE ?)';
      params.push(`%${q}%`, `%${q}%`);
    }

    if (category.trim()) {
      query += ' AND category = ?';
      params.push(category);
    }

    if (sort === 'price-asc') {
      query += ' ORDER BY price ASC';
    } else if (sort === 'price-desc') {
      query += ' ORDER BY price DESC';
    } else if (sort === 'rating') {
      query += ' ORDER BY rating DESC';
    } else {
      query += ' ORDER BY id DESC';
    }

    const products = await all(query, params);
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch products.' });
  }
});

app.get('/api/categories', async (_req, res) => {
  try {
    const categories = await all('SELECT DISTINCT category FROM products ORDER BY category ASC');
    res.json(categories.map((item) => item.category));
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch categories.' });
  }
});

app.get('/api/deals', async (_req, res) => {
  try {
    const deals = await all(`
      SELECT id, title, price, rating, image, badge
      FROM products
      WHERE badge IS NOT NULL
      ORDER BY rating DESC, price ASC
      LIMIT 4
    `);
    res.json(deals);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch deals.' });
  }
});

app.get('/api/cart', async (_req, res) => {
  try {
    const items = await all(`
      SELECT c.id, c.product_id AS productId, c.quantity, p.title, p.price, p.image
      FROM cart_items c
      JOIN products p ON p.id = c.product_id
      ORDER BY c.id DESC
    `);
    res.json(items);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch cart.' });
  }
});

app.post('/api/cart', async (req, res) => {
  const { productId } = req.body;

  if (!productId) {
    res.status(400).json({ error: 'productId is required.' });
    return;
  }

  try {
    const existing = await get('SELECT id, quantity FROM cart_items WHERE product_id = ?', [productId]);

    if (existing) {
      await run('UPDATE cart_items SET quantity = ? WHERE id = ?', [existing.quantity + 1, existing.id]);
    } else {
      await run('INSERT INTO cart_items (product_id, quantity) VALUES (?, 1)', [productId]);
    }

    res.status(201).json({ message: 'Added to cart.' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to update cart.' });
  }
});

app.delete('/api/cart/:id', async (req, res) => {
  try {
    await run('DELETE FROM cart_items WHERE id = ?', [req.params.id]);
    res.json({ message: 'Item removed.' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to remove item.' });
  }
});

app.delete('/api/cart', async (_req, res) => {
  try {
    await run('DELETE FROM cart_items');
    res.json({ message: 'Cart cleared.' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to clear cart.' });
  }
});

app.post('/api/cart/apply-coupon', async (req, res) => {
  const { code = '' } = req.body;

  if (!code.trim()) {
    res.status(400).json({ error: 'Coupon code is required.' });
    return;
  }

  try {
    const items = await all(`
      SELECT c.quantity, p.price
      FROM cart_items c
      JOIN products p ON p.id = c.product_id
    `);

    if (items.length === 0) {
      res.status(400).json({ error: 'Your cart is empty.' });
      return;
    }

    const coupon = await get('SELECT code, discount_percent AS discountPercent, min_subtotal AS minSubtotal FROM coupons WHERE code = ?', [code.trim().toUpperCase()]);

    if (!coupon) {
      res.status(404).json({ error: 'Coupon not found.' });
      return;
    }

    const totals = calculateCartTotals(items, coupon.discountPercent);

    if (totals.subtotal < coupon.minSubtotal) {
      res.status(400).json({
        error: `Coupon requires a minimum subtotal of $${coupon.minSubtotal.toFixed(2)}.`
      });
      return;
    }

    res.json({
      code: coupon.code,
      discountPercent: coupon.discountPercent,
      ...totals
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to apply coupon.' });
  }
});

app.post('/api/checkout', async (req, res) => {
  const couponCode = req.body.couponCode ? String(req.body.couponCode).trim().toUpperCase() : null;

  try {
    const items = await all(`
      SELECT c.product_id AS productId, c.quantity, p.price
      FROM cart_items c
      JOIN products p ON p.id = c.product_id
    `);

    if (items.length === 0) {
      res.status(400).json({ error: 'Cart is empty.' });
      return;
    }

    let discountPercent = 0;

    if (couponCode) {
      const coupon = await get('SELECT discount_percent AS discountPercent, min_subtotal AS minSubtotal FROM coupons WHERE code = ?', [couponCode]);

      if (!coupon) {
        res.status(404).json({ error: 'Coupon not found.' });
        return;
      }

      const preTotals = calculateCartTotals(items, coupon.discountPercent);
      if (preTotals.subtotal < coupon.minSubtotal) {
        res.status(400).json({ error: `Coupon requires a minimum subtotal of $${coupon.minSubtotal.toFixed(2)}.` });
        return;
      }

      discountPercent = coupon.discountPercent;
    }

    const totals = calculateCartTotals(items, discountPercent);
    const orderTime = new Date().toISOString();

    const result = await run(
      `INSERT INTO orders (subtotal, discount, total, coupon_code, created_at)
       VALUES (?, ?, ?, ?, ?)`,
      [totals.subtotal, totals.discount, totals.total, couponCode, orderTime]
    );

    for (const item of items) {
      await run(
        'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
        [result.lastID, item.productId, item.quantity, item.price]
      );
    }

    await run('DELETE FROM cart_items');

    res.status(201).json({
      message: 'Order placed successfully.',
      orderId: result.lastID,
      ...totals
    });
  } catch (error) {
    res.status(500).json({ error: 'Checkout failed.' });
  }
});

app.get('/api/orders', async (_req, res) => {
  try {
    const orders = await all(`
      SELECT id, subtotal, discount, total, coupon_code AS couponCode, created_at AS createdAt
      FROM orders
      ORDER BY id DESC
      LIMIT 10
    `);
    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch orders.' });
  }
});

app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api/')) {
    next();
    return;
  }

  res.sendFile(path.join(CLIENT_DIST_PATH, 'index.html'), (error) => {
    if (error) {
      res.status(503).send('Frontend not built. Run `npm run build:client` first.');
    }
  });
});

initDb()
  .then(() => {
    const server = app.listen(PORT, () => {
      // eslint-disable-next-line no-console
      console.log(`Server running on http://localhost:${PORT}`);
    });

    server.on('error', (error) => {
      if (error.code === 'EADDRINUSE') {
        // eslint-disable-next-line no-console
        console.error(`Port ${PORT} is already in use. Stop the other process or run with a different port (example: PORT=3001 yarn start).`);
        process.exit(1);
      }

      // eslint-disable-next-line no-console
      console.error('Server failed to start:', error);
      process.exit(1);
    });
  })
  .catch((error) => {
    // eslint-disable-next-line no-console
    console.error('Failed to initialize database:', error);
    process.exit(1);
  });
