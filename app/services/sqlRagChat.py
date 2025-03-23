import sqlite3
import re
import ollama

def get_db_connection():
    conn = sqlite3.connect('sample_db.db')  # Replace with your actual DB
    conn.row_factory = sqlite3.Row
    return conn

def generate_sql_query(user_question):
    # Schema information to provide context to the LLM
    schema_context = """
    Table: Contacts
    Columns:
    - id (INT, PRIMARY KEY, AUTO_INCREMENT)
    - name (VARCHAR(100))
    - rank (VARCHAR(50))
    - phone_number (VARCHAR(15))
    - address (TEXT)
    """
    
    # Updated prompt with explicit security constraints
    prompt = f"""Given the following database schema:
    {schema_context}
    
    Generate a SQL query to answer this question: "{user_question}"
    
    CRITICAL SECURITY CONSTRAINTS:
    - You MUST use ONLY SELECT statements
    - You MUST ONLY query the Contacts table
    - You MUST ONLY reference columns that exist in the schema (id, name, rank, phone_number, address)
    - You MUST include a "LIMIT 10" clause at the end of your query
    - You MUST NOT use any DDL or DML commands (CREATE, INSERT, UPDATE, DELETE, DROP, ALTER, etc.)
    
    Return ONLY the raw SQL query with NO markdown formatting, NO backticks, and NO explanations.
    """
    
    response = ollama.chat(model='mistral:7b', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ])
    
    # Extract just the SQL query from the response and clean it
    sql_query = response['message']['content'].strip()
    
    # Remove markdown code formatting if present
    if sql_query.startswith("```"):
        # Find the end of the first line to skip language identifier
        first_line_end = sql_query.find('\n')
        if first_line_end != -1:
            # Find the end of the code block
            code_end = sql_query.rfind("```")
            if code_end > first_line_end:
                # Extract just the code
                sql_query = sql_query[first_line_end+1:code_end].strip()
    
    # Additional cleanup - remove any remaining backticks
    sql_query = sql_query.replace('`', '')
    
    # Validate the SQL query for safety
    safe_query = validate_and_sanitize_sql(sql_query)
    
    return safe_query

def validate_and_sanitize_sql(sql_query):
    """
    Validate that the SQL query is safe to execute and sanitize it.
    Returns a safe parameterized query or raises an exception if the query is dangerous.
    """
    sql_lower = sql_query.lower().strip()
    
    # CONSTRAINT 1: Only allow SELECT statements
    if not sql_lower.startswith('select'):
        raise ValueError("Only SELECT queries are allowed")
    
    # CONSTRAINT 2: Check for dangerous operations
    dangerous_keywords = [
        'insert', 'update', 'delete', 'drop', 'alter', 'create',
        'truncate', 'rename', 'replace', 'exec', 'execute', 'xp_',
        'sp_', 'syscolumns', 'information_schema', '--', ';--', '/*',
        'union', 'into outfile', 'load_file'
    ]
    
    for keyword in dangerous_keywords:
        if f" {keyword} " in f" {sql_lower} " or sql_lower.startswith(keyword + " "):
            raise ValueError(f"Unsafe SQL detected: {keyword} operations are not allowed")
    
    # CONSTRAINT 3: Ensure we're only querying the Contacts table
    tables_pattern = re.compile(r'from\s+([a-zA-Z0-9_,\s]+)(?:where|group by|having|order by|limit|$)', re.IGNORECASE)
    tables_match = tables_pattern.search(sql_lower)
    
    if not tables_match:
        raise ValueError("Could not identify target tables in the query")
    
    tables_in_query = [t.strip() for t in tables_match.group(1).split(',')]
    allowed_tables = ['contacts']
    
    for table in tables_in_query:
        if table not in allowed_tables:
            raise ValueError(f"Unauthorized table in query: {table}")
    
    # CONSTRAINT 4: Validate columns against schema
    valid_columns = ['id', 'name', 'rank', 'phone_number', 'address', '*']
    
    # Extract column names from the query
    # This is a simplified version and might need enhancement for complex queries
    columns_section = sql_lower.split('select ')[1].split(' from ')[0]
    
    # Handle special cases like SELECT COUNT(*) or SELECT *
    if columns_section.strip() == '*':
        columns_used = ['*']
    else:
        columns_used = []
        for col_item in columns_section.split(','):
            col = col_item.strip()
            # Handle functions like COUNT(column) or AS aliases
            if '(' in col:
                matches = re.findall(r'([a-zA-Z0-9_]+)\s*\(', col)
                if matches and matches[0].lower() not in ['count', 'sum', 'avg', 'min', 'max']:
                    col = matches[0]
                else:
                    # Extract column from within function, e.g., COUNT(column)
                    inner_matches = re.findall(r'\(([a-zA-Z0-9_*]+)\)', col)
                    if inner_matches:
                        col = inner_matches[0]
            
            # Remove any AS aliases
            if ' as ' in col:
                col = col.split(' as ')[0].strip()
            
            columns_used.append(col)
    
    for column in columns_used:
        if column != '*' and column.lower() not in [c.lower() for c in valid_columns]:
            raise ValueError(f"Invalid column referenced: {column}")
    
    # CONSTRAINT 5: Ensure there's a LIMIT clause
    if 'limit' not in sql_lower:
        if sql_lower.endswith(';'):
            sql_query = sql_query[:-1] + " LIMIT 10;"
        else:
            sql_query = sql_query + " LIMIT 10"
    else:
        # Check if the existing LIMIT is reasonable (less than or equal to 10)
        limit_pattern = re.compile(r'limit\s+(\d+)', re.IGNORECASE)
        limit_match = limit_pattern.search(sql_lower)
        if limit_match:
            limit_value = int(limit_match.group(1))
            if limit_value > 10:
                # Replace with LIMIT 10
                sql_query = re.sub(r'LIMIT\s+\d+', 'LIMIT 10', sql_query, flags=re.IGNORECASE)
    
    return sql_query


def format_natural_language_response(user_question, results, sql_query=None):
    """
    Generate a natural language response based on the query results
    """
    # First, handle the case of no results
    if not results:
        return f"I searched for information about {user_question}, but couldn't find any matching records in the database."
    
    # For single result
    if len(results) == 1:
        result = results[0]
        if 'name' in result:
            response = f"I found one contact that matches your query. {result['name']}"
            if 'rank' in result:
                response += f" has the rank of {result['rank']}."
            if 'phone_number' in result:
                response += f" Their phone number is {result['phone_number']}."
            if 'address' in result:
                response += f" They are located at {result['address']}."
            return response
    
    # For multiple results
    response = f"I found {len(results)} contacts that match your query:"
    
    # Determine which fields to display based on the query and results
    # Simple detection of what fields might be relevant based on the question
    show_rank = 'rank' in user_question.lower() or 'position' in user_question.lower()
    show_phone = 'phone' in user_question.lower() or 'contact' in user_question.lower() or 'call' in user_question.lower()
    show_address = 'address' in user_question.lower() or 'location' in user_question.lower() or 'where' in user_question.lower()
    
    # If none of the specific fields were mentioned, show everything
    if not (show_rank or show_phone or show_address):
        show_rank = show_phone = show_address = True
    
    # Add result limit message if there are exactly 10 results
    if len(results) == 10:
        response += " (showing up to 10 results)"
    
    # Build a more detailed response for multiple results
    for i, result in enumerate(results):
        response += f"\n\n{i+1}. {result.get('name', 'Unknown')}"
        if show_rank and 'rank' in result:
            response += f" - {result['rank']}"
        if show_phone and 'phone_number' in result:
            response += f"\n   Phone: {result['phone_number']}"
        if show_address and 'address' in result:
            response += f"\n   Address: {result['address']}"
    
    return response

def answer_user_question(user_question):
    try:
        # Generate SQL query using LLM with safety validation
        sql_query = generate_sql_query(user_question)
        
        # Additional logging for debugging
        print(f"Generated SQL query: {sql_query}")
        
        try:
            # Execute the query
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Execute the query with proper error handling
            try:
                cursor.execute(sql_query)
                results = cursor.fetchall()
            except sqlite3.Error as sql_error:
                # Log the error with the query for debugging
                print(f"SQL Error: {str(sql_error)}, Query: {sql_query}")
                raise ValueError(f"Database error: {str(sql_error)}")
            finally:
                conn.close()
            
            # Format results as dictionaries
            formatted_results = [dict(row) for row in results]
            
            # Generate natural language response
            nl_response = format_natural_language_response(user_question, formatted_results, sql_query)
            
            return {
                "question": user_question,
                "sql_query": sql_query,  # Include for debugging
                "formatted_response": nl_response,
                "raw_results": formatted_results,  # Include raw results for potential further processing
                "result_count": len(formatted_results)
            }
        
        except Exception as e:
            # Catch any other errors during execution
            error_message = f"Error executing query: {str(e)}"
            return {
                "question": user_question,
                "error": str(e),
                "formatted_response": "I'm sorry, I encountered an error while retrieving the information. This issue has been logged for review."
            }
    
    except ValueError as ve:
        # Handle validation errors (likely from SQL validation)
        return {
            "question": user_question,
            "error": str(ve),
            "formatted_response": f"I'm sorry, I couldn't create a safe query for your question: {str(ve)}"
        }
    except Exception as e:
        error_message = f"I'm sorry, I encountered an error while trying to answer your question: {str(e)}"
        return {
            "question": user_question,
            "error": str(e),
            "formatted_response": error_message
        }