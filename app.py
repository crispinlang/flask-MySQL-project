## Package import:
from flask import Flask, render_template, request
from flask_mysqldb import MySQL


# initialize flask
app = Flask(__name__)
app.debug = True

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'viral_user'
app.config['MYSQL_PASSWORD'] = 'B%$RYNGQNq4$kJ%'
app.config['MYSQL_DB'] = 'viral_db'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)


@app.route("/")
def home():
    # Renders templates/home.html
    return render_template("home.html")

# This shows example Flask routes that match the navbar links and templates.
# Add these to your Flask app (app.py) if you haven't already.

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/results")
def results():
    cur = mysql.connection.cursor()

    # 1. Get all table names
    cur.execute("SHOW TABLES;")
    table_names = [row[0] for row in cur.fetchall()]

    tables = []

    for table in table_names:
        # 2. Query each table
        cur.execute(f"SELECT * FROM `{table}`;")
        rows = cur.fetchall()

        # 3. Get column names for that table
        colnames = [desc[0] for desc in cur.description]

        tables.append({
            "name": table,
            "columns": colnames,
            "rows": rows
        })

    cur.close()

    # 4. Send everything to the template
    return render_template("results.html", tables=tables)



@app.route("/testing")
def testing():
    query = request.args.get("q", "").strip()

    # Configure which columns to search and which to display per table
    TABLE_CONFIG = {
        "virus": {
            "search":  ["name", "family", "genome_type"],
            "display": ["name", "family", "genome_type"],
        },
        "genome_sequence": {
            "search":  ["accession", "length", "sequence"],
            "display": ["accession", "length", "sequence"],
        },
        "protein_sequence": {
            "search":  ["uniprot_id", "protein_name", "sequence"],
            "display": ["uniprot_id", "protein_name", "sequence"],
        },
        "enzyme_annotation": {
            "search":  ["ec_number", "enzyme_name", "source_db"],
            "display": ["ec_number", "enzyme_name", "source_db"],
        },
    }

    tables = []

    if query:
        like_value = f"%{query}%"
        cur = mysql.connection.cursor()

        for table_name, cfg in TABLE_CONFIG.items():
            search_cols = cfg["search"]
            display_cols = cfg["display"]

            # Build SELECT col1, col2, col3 ...
            select_clause = ", ".join(f"`{col}`" for col in display_cols)

            # Build WHERE colA LIKE %s OR colB LIKE %s ...
            where_clauses = " OR ".join(f"`{col}` LIKE %s" for col in search_cols)

            sql = f"SELECT {select_clause} FROM `{table_name}` WHERE {where_clauses} LIMIT 100"
            params = [like_value] * len(search_cols)

            cur.execute(sql, params)
            rows = cur.fetchall()

            if rows:
                # We already know display column order from display_cols
                tables.append({
                    "name": table_name,
                    "columns": display_cols,
                    "rows": rows,
                })

        cur.close()

    return render_template("testing.html", q=query, tables=tables)


app.run(debug=True)
