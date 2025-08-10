from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Numeric, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel, Session, select


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

    products: list["Product"] = Relationship(back_populates="category")


class Supplier(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    products: list["Product"] = Relationship(back_populates="supplier")
    purchase_orders: list["PurchaseOrder"] = Relationship(back_populates="supplier")


class Warehouse(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    location: Optional[str] = None

    stock_levels: list["StockLevel"] = Relationship(back_populates="warehouse")


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True, unique=True)
    name: str
    description: Optional[str] = None

    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    supplier_id: Optional[int] = Field(default=None, foreign_key="supplier.id")

    unit_price: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    reorder_level: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    category: Category | None = Relationship(back_populates="products")
    supplier: Supplier | None = Relationship(back_populates="products")
    stock_levels: list["StockLevel"] = Relationship(back_populates="product")
    purchase_items: list["PurchaseOrderItem"] = Relationship(back_populates="product")
    sales_items: list["SalesOrderItem"] = Relationship(back_populates="product")


class StockLevel(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uix_stocklevel_product_warehouse"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    warehouse_id: int = Field(foreign_key="warehouse.id")
    quantity: int = 0

    product: Product | None = Relationship(back_populates="stock_levels")
    warehouse: Warehouse | None = Relationship(back_populates="stock_levels")


class PurchaseOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id")
    order_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="OPEN")

    supplier: Supplier | None = Relationship(back_populates="purchase_orders")
    items: list["PurchaseOrderItem"] = Relationship(back_populates="purchase_order")


class PurchaseOrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    purchase_order_id: int = Field(foreign_key="purchaseorder.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_cost: Decimal = Field(sa_column=Column(Numeric(12, 2)))

    purchase_order: PurchaseOrder | None = Relationship(back_populates="items")
    product: Product | None = Relationship(back_populates="purchase_items")


class SalesOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    customer_name: str
    order_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="OPEN")

    items: list["SalesOrderItem"] = Relationship(back_populates="sales_order")


class SalesOrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sales_order_id: int = Field(foreign_key="salesorder.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    unit_price: Decimal = Field(sa_column=Column(Numeric(12, 2)))

    sales_order: SalesOrder | None = Relationship(back_populates="items")
    product: Product | None = Relationship(back_populates="sales_items")


class StockMovement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    warehouse_id: int = Field(foreign_key="warehouse.id")
    delta: int
    reason: str
    ref_type: Optional[str] = None  # e.g. INITIAL, PURCHASE, SALE
    ref_id: Optional[int] = None
    at: datetime = Field(default_factory=datetime.utcnow)


def _get_or_create_category(session: Session, name: str, description: Optional[str] = None) -> Category:
    category = session.exec(select(Category).where(Category.name == name)).first()
    if category:
        return category
    category = Category(name=name, description=description)
    session.add(category)
    session.flush()
    return category


def _get_or_create_supplier(session: Session, name: str, email: Optional[str] = None) -> Supplier:
    supplier = session.exec(select(Supplier).where(Supplier.name == name)).first()
    if supplier:
        return supplier
    supplier = Supplier(name=name, email=email)
    session.add(supplier)
    session.flush()
    return supplier


def _get_or_create_warehouse(session: Session, name: str, location: Optional[str] = None) -> Warehouse:
    wh = session.exec(select(Warehouse).where(Warehouse.name == name)).first()
    if wh:
        return wh
    wh = Warehouse(name=name, location=location)
    session.add(wh)
    session.flush()
    return wh


def _adjust_stock(
    session: Session,
    product: Product,
    warehouse: Warehouse,
    delta: int,
    reason: str,
    ref_type: Optional[str] = None,
    ref_id: Optional[int] = None,
) -> None:
    stock_level = session.exec(
        select(StockLevel)
        .where(StockLevel.product_id == product.id)
        .where(StockLevel.warehouse_id == warehouse.id)
    ).first()

    if stock_level is None:
        stock_level = StockLevel(product_id=product.id, warehouse_id=warehouse.id, quantity=0)
        session.add(stock_level)

    stock_level.quantity = int(stock_level.quantity) + int(delta)
    session.add(
        StockMovement(
            product_id=product.id,
            warehouse_id=warehouse.id,
            delta=delta,
            reason=reason,
            ref_type=ref_type,
            ref_id=ref_id,
        )
    )


def seed_inventory_data(session: Session) -> None:
    """
    Populate the inventory schema with dummy data if it's empty.
    Idempotent: safe to call multiple times.
    """
    # If we already have products, assume seeded
    existing_product = session.exec(select(Product).limit(1)).first()
    if existing_product:
        return

    categories = [
        ("Electronics", "Electronic devices and accessories"),
        ("Office Supplies", "Daily office consumables"),
        ("Furniture", "Office and warehouse furniture"),
        ("Grocery", "Food and beverages"),
        ("Apparel", "Clothing and uniforms"),
    ]
    suppliers = [
        ("ACME Corp", "sales@acme.example"),
        ("Globex", "hello@globex.example"),
        ("Initech", "contact@initech.example"),
    ]
    warehouses = [
        ("Central Warehouse", "HQ"),
        ("East Warehouse", "East City"),
        ("West Warehouse", "West City"),
    ]

    try:
        # Create categories, suppliers, warehouses
        category_by_name: dict[str, Category] = {}
        for name, desc in categories:
            category_by_name[name] = _get_or_create_category(session, name, desc)

        supplier_by_name: dict[str, Supplier] = {}
        for name, email in suppliers:
            supplier_by_name[name] = _get_or_create_supplier(session, name, email)

        warehouse_by_name: dict[str, Warehouse] = {}
        for name, location in warehouses:
            warehouse_by_name[name] = _get_or_create_warehouse(session, name, location)

        session.flush()

        # Products
        products_data = [
            {"sku": "ELEC-001", "name": "USB-C Cable", "category": "Electronics", "supplier": "ACME Corp", "price": Decimal("9.99")},
            {"sku": "ELEC-002", "name": "Wireless Mouse", "category": "Electronics", "supplier": "Globex", "price": Decimal("19.99")},
            {"sku": "ELEC-003", "name": "27in Monitor", "category": "Electronics", "supplier": "Initech", "price": Decimal("199.99")},
            {"sku": "OFF-001", "name": "A4 Paper Ream", "category": "Office Supplies", "supplier": "ACME Corp", "price": Decimal("4.50")},
            {"sku": "OFF-002", "name": "Ballpoint Pens (10)", "category": "Office Supplies", "supplier": "Globex", "price": Decimal("3.20")},
            {"sku": "FURN-001", "name": "Office Chair", "category": "Furniture", "supplier": "Initech", "price": Decimal("129.99")},
            {"sku": "FURN-002", "name": "Standing Desk", "category": "Furniture", "supplier": "Globex", "price": Decimal("289.00")},
            {"sku": "GROC-001", "name": "Bottled Water (24)", "category": "Grocery", "supplier": "ACME Corp", "price": Decimal("6.99")},
            {"sku": "GROC-002", "name": "Coffee Beans 1kg", "category": "Grocery", "supplier": "Globex", "price": Decimal("12.75")},
            {"sku": "APP-001", "name": "High-Vis Jacket", "category": "Apparel", "supplier": "Initech", "price": Decimal("24.90")},
            {"sku": "APP-002", "name": "Work Gloves", "category": "Apparel", "supplier": "ACME Corp", "price": Decimal("7.80")},
            {"sku": "APP-003", "name": "Steel-Toe Boots", "category": "Apparel", "supplier": "Globex", "price": Decimal("59.00")},
        ]

        products: list[Product] = []
        for p in products_data:
            product = Product(
                sku=p["sku"],
                name=p["name"],
                category_id=category_by_name[p["category"]].id,
                supplier_id=supplier_by_name[p["supplier"]].id,
                unit_price=p["price"],
                reorder_level=10,
            )
            session.add(product)
            products.append(product)

        session.flush()

        # Initial stock in Central Warehouse
        central = warehouse_by_name["Central Warehouse"]
        for product in products:
            _adjust_stock(
                session=session,
                product=product,
                warehouse=central,
                delta=50,
                reason="Initial stock",
                ref_type="INITIAL",
                ref_id=None,
            )

        # Sample purchase order (increase stock)
        po = PurchaseOrder(supplier_id=supplier_by_name["ACME Corp"].id, status="RECEIVED")
        session.add(po)
        session.flush()

        po_items = [
            ("ELEC-001", 40, Decimal("7.50")),
            ("OFF-001", 100, Decimal("3.20")),
            ("APP-002", 60, Decimal("5.00")),
        ]
        for sku, qty, cost in po_items:
            product = session.exec(select(Product).where(Product.sku == sku)).one()
            poi = PurchaseOrderItem(
                purchase_order_id=po.id, product_id=product.id, quantity=qty, unit_cost=cost
            )
            session.add(poi)
            session.flush()
            _adjust_stock(
                session=session,
                product=product,
                warehouse=central,
                delta=qty,
                reason="PO received",
                ref_type="PURCHASE",
                ref_id=po.id,
            )

        # Sample sales order (decrease stock)
        so = SalesOrder(customer_name="Demo Customer", status="SHIPPED")
        session.add(so)
        session.flush()

        so_items = [
            ("ELEC-002", 5, Decimal("24.99")),
            ("FURN-001", 2, Decimal("159.99")),
            ("GROC-001", 10, Decimal("8.50")),
        ]
        for sku, qty, price in so_items:
            product = session.exec(select(Product).where(Product.sku == sku)).one()
            soi = SalesOrderItem(
                sales_order_id=so.id, product_id=product.id, quantity=qty, unit_price=price
            )
            session.add(soi)
            session.flush()
            _adjust_stock(
                session=session,
                product=product,
                warehouse=central,
                delta=-qty,
                reason="SO shipped",
                ref_type="SALE",
                ref_id=so.id,
            )

        session.commit()
    except Exception:
        session.rollback()
        raise


__all__ = [
    "Category",
    "Supplier",
    "Warehouse",
    "Product",
    "StockLevel",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "SalesOrder",
    "SalesOrderItem",
    "StockMovement",
    "seed_inventory_data",
]


