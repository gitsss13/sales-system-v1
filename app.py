
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "v1")
sales = []
next_id = 1

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sales System {{ version }}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 850px;
            margin: 30px auto;
            padding: 20px;
            background: #f4f6f9;
        }
        .card {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
        }
        input, button {
            padding: 10px;
            margin: 6px 0;
            box-sizing: border-box;
        }
        input { width: 100%; }
        button {
            background: #17365d;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }
    </style>
</head>
<body>
    <h1>Sales Management System</h1>
    <p>Registration Number: 24MIS0356</p>
    <p>Application Version: {{ version }}</p>

    <div class="card">
        <h2>Add Sale</h2>
        <form id="saleForm">
            <label>Product Name</label>
            <input id="product" required maxlength="100">

            <label>Price per item (₹)</label>
            <input id="price" type="number"
                   min="0.01" step="0.01" required>

            <label>Quantity</label>
            <input id="quantity" type="number"
                   min="1" step="1" required>

            <button type="submit">Record Sale</button>
        </form>
        <p id="message"></p>
    </div>

    <div class="card">
        <h2>Sales Summary</h2>
        <p>Total Sales: <strong id="count">0</strong></p>
        <p>Total Items: <strong id="items">0</strong></p>
        <p>Total Revenue: <strong id="revenue">₹0.00</strong></p>
        <button onclick="loadSales()">View Sales / Refresh</button>
    </div>

    <div class="card">
        <h2>Recorded Sales</h2>
        <div style="overflow-x:auto">
            <table>
                <thead>
                    <tr>
                        <th>ID</th><th>Product</th><th>Price</th>
                        <th>Quantity</th><th>Total</th>
                    </tr>
                </thead>
                <tbody id="salesTable"></tbody>
            </table>
        </div>
    </div>

<script>
async function loadSales() {
    const response = await fetch('/api/sales');
    const data = await response.json();
    const table = document.getElementById('salesTable');
    table.replaceChildren();

    data.forEach(sale => {
        const row = document.createElement('tr');
        [sale.id, sale.product, '₹' + sale.price.toFixed(2),
         sale.quantity, '₹' + sale.total.toFixed(2)].forEach(value => {
            const cell = document.createElement('td');
            cell.textContent = value;
            row.appendChild(cell);
        });
        table.appendChild(row);
    });

    const summaryResponse = await fetch('/api/summary');
    const summary = await summaryResponse.json();

    document.getElementById('count').textContent =
        summary.total_sales;
    document.getElementById('items').textContent =
        summary.total_items;
    document.getElementById('revenue').textContent =
        '₹' + summary.total_revenue.toFixed(2);
}

document.getElementById('saleForm').addEventListener(
    'submit', async event => {
        event.preventDefault();

        const response = await fetch('/api/sales', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                product: document.getElementById('product').value,
                price: Number(document.getElementById('price').value),
                quantity: Number(
                    document.getElementById('quantity').value
                )
            })
        });

        const result = await response.json();
        document.getElementById('message').textContent =
            result.message || result.error;

        if (response.ok) {
            event.target.reset();
            await loadSales();
        }
    }
);

loadSales();
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML, version=VERSION)


@app.route("/api/sales", methods=["POST"])
def add_sale():
    global next_id

    data = request.get_json(silent=True) or {}
    product = data.get("product")
    price = data.get("price")
    quantity = data.get("quantity")

    if not isinstance(product, str) or not product.strip():
        return jsonify(error="Product name is required"), 400

    if len(product.strip()) > 100:
        return jsonify(error="Product name is too long"), 400

    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return jsonify(error="Enter a valid price"), 400

    if price <= 0 or price != price or price == float("inf"):
        return jsonify(error="Price must be positive and finite"), 400

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return jsonify(error="Quantity must be a whole number"), 400

    if quantity <= 0:
        return jsonify(error="Quantity must be positive"), 400

    price = round(price, 2)
    total = round(price * quantity, 2)

    sale = {
        "id": next_id,
        "product": product.strip(),
        "price": price,
        "quantity": quantity,
        "total": total
    }

    next_id += 1
    sales.append(sale)

    return jsonify(
        message="Sale recorded successfully!",
        sale=sale
    ), 201


@app.route("/api/sales", methods=["GET"])
def view_sales():
    return jsonify(sales)


@app.route("/api/summary", methods=["GET"])
def calculate_revenue():
    return jsonify({
        "version": VERSION,
        "total_sales": len(sales),
        "total_items": sum(sale["quantity"] for sale in sales),
        "total_revenue": round(
            sum(sale["total"] for sale in sales), 2
        )
    })


@app.route("/health")
def health():
    return jsonify(status="healthy", version=VERSION)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
