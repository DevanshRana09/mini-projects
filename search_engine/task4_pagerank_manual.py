"""
Manual PageRank calculation using iterative SQL updates.
This script uses the old_rank/new_rank ping-pong pattern.
"""

import psycopg2
import time


def init_pagerank(conn):
    """Initialize all pages with equal rank: 1.0 / total_pages."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Pages")
    total_pages = cur.fetchone()[0]

    if total_pages == 0:
        print("No pages in database. Crawl first!")
        return False

    initial_rank = 1.0 / total_pages
    cur.execute("UPDATE Pages SET old_rank = %s, new_rank = %s", (initial_rank, initial_rank))
    conn.commit()
    print(f"✓ Initialized {total_pages} pages with rank {initial_rank:.6f}")
    return True


def update_ranks_once(conn, damping_factor=0.85):
    """
    One iteration of PageRank update.
    new_rank = (1 - d) / N + d * sum(incoming_page_rank / incoming_page_outlinks)
    """
    cur = conn.cursor()

    # Get total pages for base formula
    cur.execute("SELECT COUNT(*) FROM Pages")
    N = cur.fetchone()[0]

    if N == 0:
        return 0.0

    base = (1 - damping_factor) / N

    # Update every page's new_rank based on incoming links
    # Using parameterized queries for base and damping_factor
    cur.execute("""
        UPDATE Pages
        SET new_rank = %s + %s * (
            SELECT COALESCE(SUM(src.old_rank / NULLIF(src.out_degree, 0)), 0)
            FROM Links l
            JOIN Pages src ON src.id = l.from_id
            WHERE l.to_id = Pages.id
        )
    """, (base, damping_factor))
    conn.commit()

    # Calculate max change to track convergence
    cur.execute("""
        SELECT MAX(ABS(new_rank - old_rank)) FROM Pages
    """)
    max_change = cur.fetchone()[0] or 0.0

    return max_change


def swap_ranks(conn):
    """Swap old_rank <-- new_rank for next iteration."""
    cur = conn.cursor()
    cur.execute("UPDATE Pages SET old_rank = new_rank")
    conn.commit()


def print_top_pages(conn, limit=10):
    """Print top-ranked pages."""
    cur = conn.cursor()
    cur.execute("""
        SELECT url, new_rank
        FROM Pages
        WHERE new_rank IS NOT NULL
        ORDER BY new_rank DESC
        LIMIT %s
    """, (limit,))

    print(f"\nTop {limit} pages by rank:")
    for i, (url, rank) in enumerate(cur.fetchall(), 1):
        print(f"  {i:2d}. {rank:.6f}  {url}")


def calculate_pagerank_manual(db_host, db_user, db_password, db_name,
                              max_iterations=50, damping_factor=0.85,
                              convergence_threshold=0.0001):
    """
    Main PageRank calculation loop.

    Args:
        max_iterations: max rounds to iterate (e.g., 50)
        damping_factor: probability of following a link (e.g., 0.85)
        convergence_threshold: stop if max_change < this (e.g., 0.0001)
    """

    conn = psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    print("=" * 60)
    print("PageRank Calculation (Manual Iteration)")
    print("=" * 60)

    # Initialize
    if not init_pagerank(conn):
        conn.close()
        return

    print(f"\nParameters:")
    print(f"  - Damping factor: {damping_factor}")
    print(f"  - Convergence threshold: {convergence_threshold}")
    print(f"  - Max iterations: {max_iterations}")

    start_time = time.time()

    print("\nIterating...")
    for iteration in range(1, max_iterations + 1):
        max_change = update_ranks_once(conn, damping_factor)
        swap_ranks(conn)

        print(f"  Iteration {iteration:3d}: max change = {max_change:.8f}", end="")

        if max_change < convergence_threshold:
            print(f" ✓ CONVERGED")
            break
        else:
            print()

    elapsed = time.time() - start_time
    print(f"\n✓ Completed in {elapsed:.2f}s")

    # Show results
    print_top_pages(conn, limit=15)

    conn.close()


def main():
    print("\n" + "=" * 60)
    print("PostgreSQL PageRank Calculator (Manual)")
    print("=" * 60 + "\n")

    # Get DB connection params
    db_host = input("Enter PostgreSQL host [default: localhost]: ").strip() or "localhost"
    db_user = input("Enter PostgreSQL user [default: postgres]: ").strip() or "postgres"
    db_password = input("Enter PostgreSQL password [default: password]: ").strip() or "password"
    db_name = input("Enter PostgreSQL database name [default: spider_db]: ").strip() or "spider_db"

    max_iterations_str = input("Enter max iterations [default: 50]: ").strip()
    max_iterations = int(max_iterations_str) if max_iterations_str else 50

    damping_str = input("Enter damping factor [default: 0.85]: ").strip()
    damping = float(damping_str) if damping_str else 0.85

    convergence_str = input("Enter convergence threshold [default: 0.0001]: ").strip()
    convergence = float(convergence_str) if convergence_str else 0.0001

    calculate_pagerank_manual(
        db_host=db_host,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        max_iterations=max_iterations,
        damping_factor=damping,
        convergence_threshold=convergence
    )


if __name__ == "__main__":
    main()

