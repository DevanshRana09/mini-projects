"""
PageRank calculation using NetworkX library.
This is a fast, validated approach using a mature library.
"""

import psycopg2
import networkx as nx
import time


def calculate_pagerank_networkx(db_host, db_user, db_password, db_name,
                                 damping_factor=0.85, max_iterations=100):
    """
    Calculate PageRank using NetworkX.

    Args:
        max_iterations: max iterations for the algorithm
        damping_factor: probability of following a link (e.g., 0.85)
    """

    conn = psycopg2.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    print("=" * 60)
    print("PageRank Calculation (NetworkX)")
    print("=" * 60)

    cur = conn.cursor()

    # Get page count
    cur.execute("SELECT COUNT(*) FROM Pages")
    page_count = cur.fetchone()[0]

    if page_count == 0:
        print("No pages in database. Crawl first!")
        conn.close()
        return

    print(f"\nLoading graph from database...")
    print(f"  - Total pages: {page_count}")

    start_time = time.time()

    # Create directed graph
    G = nx.DiGraph()

    # Add all nodes (pages)
    cur.execute("SELECT id FROM Pages")
    nodes = [row[0] for row in cur.fetchall()]
    G.add_nodes_from(nodes)

    # Add all edges (links)
    cur.execute("SELECT from_id, to_id FROM Links")
    edges = cur.fetchall()
    G.add_edges_from(edges)

    edge_count = len(edges)
    print(f"  - Total links: {edge_count}")

    load_time = time.time() - start_time
    print(f"  - Load time: {load_time:.3f}s")

    print(f"\nParameters:")
    print(f"  - Damping factor: {damping_factor}")
    print(f"  - Max iterations: {max_iterations}")

    # Calculate PageRank
    print(f"\nCalculating PageRank...")
    calc_start = time.time()

    scores = nx.pagerank(G, alpha=damping_factor, max_iter=max_iterations)

    calc_time = time.time() - calc_start
    print(f"✓ Calculated in {calc_time:.3f}s")

    # Update database with new_rank
    print(f"\nUpdating database with ranks...")
    update_start = time.time()

    cur.execute("UPDATE Pages SET new_rank = 0.0")  # Reset first

    for page_id, rank in scores.items():
        cur.execute("UPDATE Pages SET new_rank = %s WHERE id = %s", (rank, page_id))

    conn.commit()

    update_time = time.time() - update_start
    print(f"✓ Updated database in {update_time:.3f}s")

    # Print stats
    print(f"\nRank statistics:")
    rank_values = list(scores.values())
    print(f"  - Min rank: {min(rank_values):.8f}")
    print(f"  - Max rank: {max(rank_values):.8f}")
    print(f"  - Mean rank: {sum(rank_values) / len(rank_values):.8f}")

    # Print top pages
    print(f"\nTop 15 pages by rank:")
    cur.execute("""
        SELECT id, url, new_rank
        FROM Pages
        ORDER BY new_rank DESC
        LIMIT 15
    """)

    for i, (page_id, url, rank) in enumerate(cur.fetchall(), 1):
        print(f"  {i:2d}. {rank:.6f}  {url}")

    conn.close()

    total_time = time.time() - start_time
    print(f"\n✓ Total time: {total_time:.2f}s")



def main():
    print("\n" + "=" * 60)
    print("PostgreSQL PageRank Calculator (NetworkX)")
    print("=" * 60 + "\n")

    # Get DB connection params
    db_host = input("Enter PostgreSQL host [default: localhost]: ").strip() or "localhost"
    db_user = input("Enter PostgreSQL user [default: postgres]: ").strip() or "postgres"
    db_password = input("Enter PostgreSQL password [default: password]: ").strip() or "password"
    db_name = input("Enter PostgreSQL database name [default: spider_db]: ").strip() or "spider_db"

    max_iterations_str = input("Enter max iterations [default: 100]: ").strip()
    max_iterations = int(max_iterations_str) if max_iterations_str else 100

    damping_str = input("Enter damping factor [default: 0.85]: ").strip()
    damping = float(damping_str) if damping_str else 0.85

    calculate_pagerank_networkx(
        db_host=db_host,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        damping_factor=damping,
        max_iterations=max_iterations
    )



if __name__ == "__main__":
    main()

