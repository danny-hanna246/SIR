from flask import Flask, render_template, request
import search

app = Flask(__name__, template_folder="templates")


@app.route('/', methods=['GET', 'POST'])
def search_documents():
    if request.method == 'GET':
        return render_template('index.html')

    # Extract query and algorithm from the form
    query = request.form.get('query')
    algorithm = request.form.get('algorithm')

    # Check for missing query
    if not query:
        error_message = "Please enter a search query."
        return render_template('index.html', error_message=error_message)

    # Check for invalid algorithm
    if algorithm not in ("BM", "EBM", "VM"):
        error_message = "Invalid search algorithm selected."
        return render_template('index.html', error_message=error_message)

    try:
        documents = search.get_documents()
        results = search.search(query, documents, algorithm)
    except Exception as e:
        # Handle any unexpected errors during search
        error_message = "An error occurred during search: " + str(e)
        return render_template('index.html', error_message=error_message)

    return render_template('results.html', query=query, algorithm=algorithm, results=results)


@app.route('/documents')
def get_documents():
    try:
        documents = search.get_documents()
    except Exception as e:
        # Handle any unexpected errors while retrieving documents
        error_message = "An error occurred while retrieving documents: " + str(e)
        return render_template('documents.html', error_message=error_message)

    return render_template('documents.html', documents=documents)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
