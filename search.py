import math
import sqlite3
import arabert
import nltk
import textblob
from contextlib import closing


def detect_language(text):
    """
    This function detects the language of the provided text using the TextBlob library.

    Args:
        text (str): The text whose language needs to be identified.

    Returns:
        str: The ISO code of the detected language.
    """

    # Create a TextBlob object from the input text
    text_blob = textblob.TextBlob(text)

    # Use the TextBlob library's built-in language detection function
    detected_language = text_blob.detect_language()

    # Return the ISO code of the detected language
    return detected_language.iso_code


def preprocess_text(text, language):
    """
    This function preprocesses the input text for indexing based on the specified language.

    Args:
        text (str): The text to be preprocessed.
        language (str): The language of the text, either 'en' for English or 'ar' for Arabic.

    Returns:
        str: The preprocessed text suitable for indexing.
    """

    preprocessed_text = None

    # Perform language-specific preprocessing based on the provided language
    if language == 'en':
        # English text preprocessing steps:
        # 1. Tokenize the text into individual words
        tokens = nltk.word_tokenize(text)
        # 2. Stem each word using Porter Stemmer
        stemmed_tokens = [nltk.stem.PorterStemmer().stem(token) for token in tokens]
        # 3. Remove stop words from the token list
        filtered_tokens = [token for token in stemmed_tokens if token not in nltk.corpus.stopwords.words('english')]
        # 4. Join the filtered tokens back into a single string
        preprocessed_text = ' '.join(filtered_tokens)
    elif language == 'ar':
        # Arabic text preprocessing steps:
        # 1. Tokenize the text into individual words
        tokens = nltk.word_tokenize(text)
        # 2. Stem each word using Snowball Stemmer for Arabic
        stemmer = nltk.stem.snowball.SnowballStemmer(language='arabic')
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        # 3. Filter out stop words using arabert's is_stop_word function
        filtered_tokens = [token for token in stemmed_tokens if not arabert.is_stop_word(token)]
        # 4. Join the filtered tokens back into a single string
        preprocessed_text = ' '.join(filtered_tokens)

    return preprocessed_text


def index_document(filename, text, language):
    """
    This function indexes a document into the database with the provided filename, text, and language.

    Args:
        filename (str): The filename of the document.
        text (str): The text content of the document.
        language (str): The language of the document, either 'en' for English or 'ar' for Arabic.

    Returns:
        None
    """

    try:
        # Connect to the SQLite database using a context manager for automatic closing
        with closing(sqlite3.connect('index.db')) as connection:
            # Create a cursor object for executing database queries
            cursor = connection.cursor()

            # Execute the SQL statement to insert the document into the database
            cursor.execute('INSERT INTO documents (filename, text, language) VALUES (?, ?, ?)',
                           (filename, text, language))

            # Commit changes to the database
            connection.commit()
    except Exception as e:
        # Print an error message if any exception occurs during indexing
        print(f"Error indexing document: {e}")
    finally:
        # Ensure the connection is closed even if an exception occurs
        if connection:
            connection.close()


def get_documents():
    """
    This function retrieves all indexed documents from the database.

    Returns:
        list: A list of dictionaries containing document information.
    """

    # Connect to the SQLite database
    connection = sqlite3.connect('index.db')

    # Create a cursor object for executing database queries
    cursor = connection.cursor()

    # Execute the SQL statement to retrieve all documents from the database
    cursor.execute('SELECT * FROM documents')

    # Fetch all results as a list of dictionaries
    documents = cursor.fetchall()

    # Close the database connection
    connection.close()

    return documents


def create_document_vectors(documents):
    """
    This function creates document vectors for each indexed document, representing the term frequencies of each word.

    Args:
        documents (list): A list of dictionaries containing document information.

    Returns:
        dict: A dictionary where keys are filenames and values are dictionaries mapping terms to their frequencies.
    """

    document_vectors = {}
    for doc in documents:
        # Preprocess the document text based on its language
        preprocessed_text = preprocess_text(doc['text'], doc['language'])

        # Tokenize the preprocessed text into individual terms
        tokens = preprocessed_text.split()

        # Initialize a dictionary to store term frequencies
        term_counts = {}

        # Count the frequency of each term in the document
        for term in tokens:
            if term in term_counts:
                term_counts[term] += 1
            else:
                term_counts[term] = 1

        # Store the term frequency dictionary for the current document
        document_vectors[doc['filename']] = term_counts

    return document_vectors


def calculate_tf(term, document):
    """
    Calculates the term frequency (tf) for a term in a document.

    Args:
        term (str): The term to be analyzed.
        document (str): The document text.

    Returns:
        int: The frequency of the term in the document.
    """
    tf = 0
    for token in document.split():
        if token == term:
            tf += 1
    return tf


def calculate_idf(term, documents):
    """
    Calculates the inverse document frequency (idf) for a term across all documents.

    Args:
        term (str): The term to be analyzed.
        documents (list): A list of document strings.

    Returns:
        float: The idf score for the term.
    """
    num_docs_containing_term = 0
    for document in documents:
        if term in document:
            num_docs_containing_term += 1

    if num_docs_containing_term == 0:
        idf = math.log(len(documents) + 1)
    else:
        idf = math.log(len(documents) / num_docs_containing_term)
    return idf


def calculate_tf_idf(term, document, documents):
    """
    Calculates the TF-IDF weight for a term in a document.

    Args:
        term (str): The term to be analyzed.
        document (str): The document text.
        documents (list): A list of document strings.

    Returns:
        float: The tf-idf weight for the term.
    """
    tf = calculate_tf(term, document)
    idf = calculate_idf(term, documents)
    return tf * idf


def calculate_document_length(document):
    """
    Calculates the document length (number of terms) in a document.

    Args:
        document (str): The document text.

    Returns:
        int: The length of the document.
    """
    return len(document.split())


def calculate_cosine_similarities(query_vector, document_vectors):
    """
    Calculates the cosine similarity between a query vector and all document vectors, representing the relevance of
    each document to the query.

    Args: query_vector (dict): A dictionary mapping terms to their TF-IDF weights in the query. document_vectors (
    dict): A dictionary where keys are filenames and values are dictionaries mapping terms to their TF-IDF weights in
    each document.

    Returns: dict: A dictionary where keys are filenames and values are cosine similarity scores between the query
    and each document.
    """

    cosine_similarities = {}
    for filename, doc_vector in document_vectors.items():
        doc_terms = doc_vector.keys()
        doc_weights = doc_vector.values()

        # Calculating the dot product
        dot_product = sum(query_vector.get(term, 0) * doc_vector.get(term, 0) for term in doc_terms)

        # Calculating the norms
        norm_query = sum(weight ** 2 for weight in query_vector.values()) ** 0.5
        norm_document = sum(weight ** 2 for weight in doc_weights) ** 0.5

        if norm_query > 0 and norm_document > 0:
            cosine_similarities[filename] = dot_product / (norm_query * norm_document)
        else:
            cosine_similarities[filename] = 0.0

    return cosine_similarities


def rank_documents(documents, scores):
    """
    This function ranks documents based on their cosine similarity scores to the query, from most relevant to least
    relevant.

    Args: documents (list): A list of dictionaries containing document information. scores (dict): A dictionary where
    keys are filenames and values are cosine similarity scores between the query and each document.

    Returns:
        list: A list of dictionaries containing document information sorted by their relevance to the query.
    """

    # Sort documents based on their scores in descending order (most relevant first)
    ranked_documents = sorted(documents, key=lambda doc: scores[doc['filename']], reverse=True)

    return ranked_documents


def is_relevant_bm(query, document):
    """
    This function checks if a document is relevant to a query using the Boolean Model (BM) search logic.

    Args:
        query (str): The search query.
        document (dict): A dictionary containing document text with key 'text'.

    Returns:
        bool: True if the document is relevant to the query, False otherwise.
    """
    terms = query.split()
    return all(term in document['text'] for term in terms)


def is_relevant_ebm(query, document):
    """
    This function checks if a document is relevant to a query using the Extended Boolean Model (EBM) search logic.

    Args:
        query (str): The search query.
        document (dict): A dictionary containing document text with key 'text'.

    Returns:
        bool: True if the document is relevant to the query, False otherwise.
    """
    terms = query.split()
    return any(term in document['text'] for term in terms)


def create_query_vector(query):
    """
    This function creates a vector representation of the query by counting the frequency of each term after
    preprocessing.

    Args:
        query (str): The search query.

    Returns:
        dict: A dictionary mapping each term in the query to its frequency.
    """

    # Preprocess the query text for English language
    preprocessed_query = preprocess_text(query, 'en')

    # Tokenize the preprocessed query into individual terms
    tokens = preprocessed_query.split()

    # Initialize a dictionary to store term frequencies
    term_counts = {}

    # Count the frequency of each term in the query
    for term in tokens:
        if term in term_counts:
            term_counts[term] += 1
        else:
            term_counts[term] = 1

    # Create the query vector based on the term frequencies
    query_vector = term_counts

    return query_vector


def search(query, documents, algorithm):
    """
    This function searches the indexed documents for those relevant to the provided query using the specified search
    algorithm.

    Args:
        query (str): The search query.
        documents (list): A list of dictionaries containing document information.
        algorithm (str): The search algorithm to be used (BM, EBM, or VM).

    Returns: list: A list of dictionaries containing information about relevant documents, or None if the algorithm
    is invalid.
    """

    if algorithm == "BM":
        # Implement Boolean Model search logic
        # Iterate through documents and check for presence of all query terms
        relevant_docs = []
        for document in documents:
            if is_relevant_bm(query, document):
                relevant_docs.append(document)
        return relevant_docs

    elif algorithm == "EBM":
        # Implement Extended Boolean Model search logic
        # Iterate through documents and check for presence of at least one query term
        relevant_docs = []
        for document in documents:
            if is_relevant_ebm(query, document):
                relevant_docs.append(document)
        return relevant_docs

    elif algorithm == "VM":
        # Implement Vector Model search logic
        # Create document vectors and query vector
        document_vectors = create_document_vectors(documents)
        query_vector = create_query_vector(query)

        # Calculate cosine similarities between query and each document
        scores = calculate_cosine_similarities(query_vector, document_vectors)

        # Rank documents based on their cosine similarities
        ranked_documents = rank_documents(documents, scores)

        return ranked_documents

    else:
        print("Invalid algorithm:", algorithm)
        return None
