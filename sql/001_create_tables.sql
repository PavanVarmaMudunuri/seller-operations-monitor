CREATE TABLE IF NOT EXISTS seller (
    seller_id VARCHAR(30) PRIMARY KEY,
    seller_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL,
    join_date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    commission_tier VARCHAR(30) NOT NULL,
    reserve_rate NUMERIC(8,6) NOT NULL
);

CREATE TABLE IF NOT EXISTS product_listing (
    listing_id VARCHAR(60) PRIMARY KEY,
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    product_id VARCHAR(40) NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(250) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price NUMERIC(12,2) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    listing_status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
    customer_id VARCHAR(30) PRIMARY KEY,
    region VARCHAR(80) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(30) NOT NULL REFERENCES customer(customer_id),
    order_date DATE NOT NULL,
    currency CHAR(3) NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    gross_amount NUMERIC(14,2) NOT NULL,
    discount_amount NUMERIC(14,2) NOT NULL,
    shipping_amount NUMERIC(14,2) NOT NULL,
    tax_amount NUMERIC(14,2) NOT NULL,
    net_order_amount NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_line (
    order_line_id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL REFERENCES orders(order_id),
    listing_id VARCHAR(60) NOT NULL REFERENCES product_listing(listing_id),
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(12,2) NOT NULL,
    discount_amount NUMERIC(12,2) NOT NULL,
    line_total NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS fulfillment (
    fulfillment_id VARCHAR(80) PRIMARY KEY,
    order_line_id VARCHAR(50) NOT NULL REFERENCES order_line(order_line_id),
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    fulfillment_status VARCHAR(30) NOT NULL,
    promised_ship_date DATE NOT NULL,
    actual_ship_date DATE,
    promised_delivery_date DATE NOT NULL,
    actual_delivery_date DATE,
    carrier VARCHAR(50),
    tracking_number VARCHAR(100),
    return_status VARCHAR(30) NOT NULL,
    sla_status VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS customer_review (
    review_id VARCHAR(40) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL REFERENCES orders(order_id),
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    rating INTEGER NOT NULL,
    review_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS dispute (
    dispute_id VARCHAR(30) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL REFERENCES orders(order_id),
    order_line_id VARCHAR(50) NOT NULL REFERENCES order_line(order_line_id),
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    dispute_type VARCHAR(40) NOT NULL,
    status VARCHAR(30) NOT NULL,
    dispute_amount NUMERIC(14,2) NOT NULL,
    opened_date DATE NOT NULL,
    resolved_date DATE,
    financially_applicable BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS commission_rule (
    commission_rule_id VARCHAR(40) PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    commission_tier VARCHAR(30) NOT NULL,
    commission_rate NUMERIC(8,6) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE
);

CREATE TABLE IF NOT EXISTS payout (
    payout_id VARCHAR(40) PRIMARY KEY,
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    payout_date DATE NOT NULL,
    total_amount NUMERIC(14,2) NOT NULL,
    eligibility_status VARCHAR(30) NOT NULL,
    exception_code VARCHAR(80)
);

CREATE TABLE IF NOT EXISTS payout_line (
    payout_line_id VARCHAR(60) PRIMARY KEY,
    payout_id VARCHAR(40) NOT NULL REFERENCES payout(payout_id),
    order_line_id VARCHAR(50) NOT NULL REFERENCES order_line(order_line_id),
    gross_amount NUMERIC(14,2) NOT NULL,
    commission_amount NUMERIC(14,2) NOT NULL,
    refund_amount NUMERIC(14,2) NOT NULL,
    dispute_deduction NUMERIC(14,2) NOT NULL,
    reserve_amount NUMERIC(14,2) NOT NULL,
    net_payout_amount NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS seller_status_event (
    event_id VARCHAR(50) PRIMARY KEY,
    seller_id VARCHAR(30) NOT NULL REFERENCES seller(seller_id),
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    effective_at TIMESTAMP NOT NULL,
    reason VARCHAR(200) NOT NULL
);
