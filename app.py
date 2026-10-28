
from flask import Flask, request, jsonify, render_template_string
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "v2")
sales = []
next_id = 1

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sales Management System - V2</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            color: #1e293b;
        }

        header {
            background: #17365d;
            color: white;
            padding: 24px;
        }

        header h1 {
            margin: 0 0 8px;
        }

        header p {
            margin: 0;
            color: #dbeafe;
        }

        main {
            max-width: 1100px;
            margin: 25px auto;
            padding: 0 18px;
        }

        .version {
            display: inline-block;
            background: #dbeafe;
            color: #17365d;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 12px;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }

        .card {
            background: white;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 3px 12px rgba(15, 23, 42, 0.07);
            margin-bottom: 22px;
        }

        .summary .card {
            border-left: 5px solid #2563eb;
            margin-bottom: 0;
        }

        .summary h3 {
            color: #64748b;
            margin: 0 0 12px;
            font-size: 15px;
        }

        .summary strong {
            font-size: 25px;
        }

        h2 {
            margin-top: 0;
            color: #17365d;
        }

        label {
            display: block;
            margin-top: 13px;
            font-weight: bold;
        }

        input {
            display: block;
            width: 100%;
            padding: 12px;
            margin-top: 7px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
            font-size: 15px;
        }

        button {
            padding: 11px 16px;
            border: none;
            border-radius: 7px;
            background: #2563eb;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin-top: 15px;
        }

        button:hover {
            background: #1d4ed8;
        }

        .secondary {
            background: #475569;
        }

        .message {
            margin-top: 12px;
            font-weight: bold;
        }

        .table-wrapper {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 14px;
        }

        th, td {
            padding: 13px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #eff6ff;
            color: #17365d;
        }

        .empty {
            text-align: center;
            color: #64748b;
            padding: 25px;
        }

        footer {
            text-align: center;
            padding: 22px;
            color: #64748b;
        }

        @media (max-width: 600px) {
            header {
                padding: 18px;
            }

            .summary strong {
                font-size: 22px;
            }
        }
    </style>
</head>

<body>
    <header>
        <h1>Sales Management System</h1>
        <p>Record sales, monitor transactions and track revenue.</p>
        <span class="version">VERSION {{ version }}</span>
        <p style="margin-top: 12px;">
            Registration Number: 24MIS0356
        </p>
    </header>

    <main>
        <section class="summary">
            <div class="card">
                <h3>Total Revenue</h3>
                <strong id="revenue">₹0.00</strong>
            </div>

            <div class="card">
                <h3>Total Sales</h3>
                <strong id="count">0</strong>
            </div>

            <div class="card">
                <h3>Items Sold</h3>
                <strong id="items">0</strong>
            </div>
        </section>

        <section class="card">
            <h2>Add New Sale</h2>

            <form id="saleForm">
                <label for="product">Product Name</label>
                <input id="product" maxlength="100"
                       placeholder="Enter product name" required>

                <label for="price">Price per Item (₹)</label>
                <input id="price" type="number" min="0.01"
                       step="0.01" placeholder="Enter price" required>

                <label for="quantity">Quantity</label>
                <input id="quantity" type="number" min="1"
                       step="1" placeholder="Enter quantity" required>

                <button type="submit">Record Sale</button>
            </form>

            <p id="message" class="message" role="status"></p>
        </section>

        <section class="card">
            <h2>Sales History</h2>

            <label for="search">Search by Product</label>
            <input id="search"
                   placeholder="Type a product name to filter sales">

            <button type="button" id="refresh" class="secondary">
                Refresh Sales
            </button>

            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Sale ID</th>
                            <th>Product</th>
                            <th>Unit Price</th>
                            <th>Quantity</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody id="salesTable">
                        <tr>
                            <td colspan="5" class="empty">
                                No sales recorded yet.
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
    </main>

    <footer>
        Sales Management System · {{ version }}
    </footer>

    <script>
        const money = value =>
            "₹" + Number(value).toFixed(2);

        async function loadSales() {
            try {
                const response = await fetch("/api/sales");

                if (!response.ok) {
                    throw new Error("Unable to load sales.");
                }

                const data = await response.json();

                const summaryResponse = await fetch("/api/summary");

                if (!summaryResponse.ok) {
                    throw new Error("Unable to load summary.");
                }

                const summary = await summaryResponse.json();

                document.getElementById("revenue").textContent =
                    money(summary.total_revenue);

                document.getElementById("count").textContent =
                    summary.total_sales;

                document.getElementById("items").textContent =
                    summary.total_items;

                const searchTerm = document
                    .getElementById("search")
                    .value.trim().toLowerCase();

                const filtered = data.filter(sale =>
                    sale.product.toLowerCase().includes(searchTerm)
                );

                const table = document.getElementById("salesTable");
                table.replaceChildren();

                if (filtered.length === 0) {
                    const row = document.createElement("tr");
                    const cell = document.createElement("td");

                    cell.colSpan = 5;
                    cell.className = "empty";
                    cell.textContent = data.length === 0
                        ? "No sales recorded yet."
                        : "No matching products found.";

                    row.appendChild(cell);
                    table.appendChild(row);
                    return;
                }

                filtered.forEach(sale => {
                    const row = document.createElement("tr");

                    [
                        sale.id,
                        sale.product,
                        money(sale.price),
                        sale.quantity,
                        money(sale.total)
                    ].forEach(value => {
                        const cell = document.createElement("td");
                        cell.textContent = value;
                        row.appendChild(cell);
                    });

                    table.appendChild(row);
                });
            } catch (error) {
                document.getElementById("message").textContent =
                    error.message;
            }
        }

        document.getElementById("saleForm").addEventListener(
            "submit", async event => {
                event.preventDefault();

                const message = document.getElementById("message");
                message.textContent = "Recording sale...";

                try {
                    const response = await fetch("/api/sales", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            product: document.getElementById("product").value,
                            price: Number(
                                document.getElementById("price").value
                            ),
                            quantity: Number(
                                document.getElementById("quantity").value
                            )
                        })
                    });

                    const result = await response.json();

                    if (!response.ok) {
                        throw new Error(result.error || "Sale failed.");
                    }

                    message.textContent = result.message;
                    event.target.reset();
                    await loadSales();
                } catch (error) {
                    message.textContent = error.message;
                }
            }
        );

        document.getElementById("search").addEventListener(
            "input", loadSales
        );

        document.getElementById("refresh").addEventListener(
            "click", loadSales
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
        return jsonify(error="Product name is required."), 400

    product = product.strip()

    if len(product) > 100:
        return jsonify(error="Product name cannot exceed 100 characters."), 400

    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return jsonify(error="Enter a valid price."), 400

    if isinstance(price, float) and not __import__("math").isfinite(price):
        return jsonify(error="Price must be finite."), 400

    if price <= 0:
        return jsonify(error="Price must be greater than zero."), 400

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return jsonify(error="Quantity must be a whole number."), 400

    if quantity <= 0:
        return jsonify(error="Quantity must be greater than zero."), 400

    try:
        unit_price = Decimal(str(price)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total = (unit_price * quantity).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    except (InvalidOperation, ValueError):
        return jsonify(error="Invalid price or quantity."), 400

    sale = {
        "id": next_id,
        "product": product,
        "price": float(unit_price),
        "quantity": quantity,
        "total": float(total)
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
    total_revenue = sum(
        (Decimal(str(sale["total"])) for sale in sales),
        Decimal("0.00")
    )

    return jsonify({
        "version": VERSION,
        "total_sales": len(sales),
        "total_items": sum(sale["quantity"] for sale in sales),
        "total_revenue": float(
            total_revenue.quantize(Decimal("0.01"))
        )
    })


@app.route("/health")
def health():
    return jsonify(status="healthy", version=VERSION)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
