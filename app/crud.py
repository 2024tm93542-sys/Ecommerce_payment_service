from .db import get_connection
import random
import secrets
from datetime import datetime


def fetch_payments(
    page=1,
    per_page=10,
    order_id=None,
    method=None,
    status=None,
    amount_gt=None,
    amount_lt=None,
    start_date=None,
    end_date=None,
    sort_by_created: str = "desc",
):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM payments WHERE 1=1"
    count_query = "SELECT COUNT(*) as total FROM payments WHERE 1=1"
    params = []
    count_params = []

    if order_id is not None:
        query += " AND order_id = %s"
        count_query += " AND order_id = %s"
        params.append(order_id)
        count_params.append(order_id)

    if method:
        query += " AND method = %s"
        count_query += " AND method = %s"
        params.append(method)
        count_params.append(method)

    if status is not None:
        # accept textual status values (SUCCESS/FAILED/1/0/true/false)
        s = str(status).strip().lower()
        if s in ("1", "true", "success", "yes"):
            status_val = 1
        else:
            status_val = 0
        query += " AND status = %s"
        count_query += " AND status = %s"
        params.append(status_val)
        count_params.append(status_val)

    if amount_gt is not None:
        query += " AND amount >= %s"
        count_query += " AND amount >= %s"
        params.append(amount_gt)
        count_params.append(amount_gt)

    if amount_lt is not None:
        query += " AND amount <= %s"
        count_query += " AND amount <= %s"
        params.append(amount_lt)
        count_params.append(amount_lt)

    if start_date:
        query += " AND created_at >= %s"
        count_query += " AND created_at >= %s"
        params.append(start_date)
        count_params.append(start_date)

    if end_date:
        query += " AND created_at <= %s"
        count_query += " AND created_at <= %s"
        params.append(end_date)
        count_params.append(end_date)

    # sorting
    order_clause = "DESC" if sort_by_created.lower() != "asc" else "ASC"
    query += f" ORDER BY created_at {order_clause}"

    # pagination
    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.execute(count_query, count_params)
    total = cursor.fetchone()["total"]

    conn.close()
    return rows, total


def create_payment_probabilistic(order_id: int, amount: float):
    """Create a payment row with probabilistic/random method and status.

    Returns the inserted payment row (dictionary) including payment_id and reference.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    method = random.choice(["COD", "CARD", "UPI"])
    # probabilistic boolean status stored as 1 (success) or 0 (failed)
    status_bool = 1 if random.random() < 0.6 else 0
    # random reference suffix
    suffix = secrets.token_hex(4).upper()
    reference = f"ECI20250910-{suffix}"
    created_at = datetime.now()

    cursor.execute(
        """INSERT INTO payments 
           (order_id, amount, method, status, reference, created_at, refunded) 
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (order_id, amount, method, status_bool, reference, created_at, 0)
    )
    conn.commit()
    payment_id = cursor.lastrowid

    # fetch the inserted row
    cursor.execute("SELECT * FROM payments WHERE payment_id=%s", (payment_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def fetch_payment_by_id(payment_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM payments WHERE payment_id=%s", (payment_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def refund_payment(payment_id: int):
    """Idempotent refund: if payment.status == 'SUCCESS' -> set 'REFUNDED' and return amount/method.
    If already 'REFUNDED', return same amount/method (idempotent). If payment failed, return None.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT payment_id, amount, method, status FROM payments WHERE payment_id=%s", (payment_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    status = row.get("status")
    refunded = row.get("refunded")
    # If already refunded, return idempotent result
    if refunded:
        result = {"payment_id": payment_id, "amount": row["amount"], "method": row["method"]}
        conn.close()
        return result

    # Only allow refund when original status indicates success (1)
    if status == 1:
        cursor.execute("UPDATE payments SET refunded=%s WHERE payment_id=%s", (1, payment_id))
        conn.commit()
        result = {"payment_id": payment_id, "amount": row["amount"], "method": row["method"]}
        conn.close()
        return result

    # payment failed -> cannot refund
    conn.close()
    return False
