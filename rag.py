import os
import glob
import argparse
from openai import OpenAI
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def get_openai_embedding(text):
    """Generate embeddings using OpenAI's API"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding


def load_markdown_files(directory="data"):
    """Load all markdown files from the specified directory"""
    markdown_files = glob.glob(os.path.join(directory, "*.md"))
    documents = []

    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

                # Skip empty files
                if not content.strip():
                    continue

                # Create a document with the file content
                file_name = os.path.basename(file_path)
                doc_id = os.path.splitext(file_name)[0]  # Remove .md extension

                documents.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": {
                        "source": file_path,
                        "title": doc_id.replace('-', ' ').title()
                    }
                })
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    return documents


def initialize_chroma_db(documents):
    """Initialize ChromaDB with document embeddings"""
    print(f"Processing {len(documents)} documents for embeddings...")

    # Extract data for ChromaDB
    embeddings = []
    contents = []
    metadatas = []
    ids = []

    for doc in documents:
        try:
            # Generate embedding
            embedding = get_openai_embedding(doc["content"])

            # Store document info
            embeddings.append(embedding)
            contents.append(doc["content"])
            metadatas.append(doc["metadata"])
            ids.append(doc["id"])

            print(f"✅ Generated embedding for {doc['id']}")
        except Exception as e:
            print(f"❌ Error generating embedding for {doc['id']}: {e}")

    # Create ChromaDB collection
    client = chromadb.Client()

    # Check if collection exists and delete if it does
    try:
        client.delete_collection("history_knowledge_base")
        print("Deleted existing collection")
    except:
        pass

    collection = client.create_collection("history_knowledge_base")

    # Add documents to collection
    if embeddings:
        print(f"Adding {len(embeddings)} documents to ChromaDB...")
        collection.add(
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        print("✅ Successfully added documents to ChromaDB")
    else:
        print("❌ No embeddings were generated. Please check your OpenAI API key.")

    return collection


def query_knowledge_base(collection, query_text, n_results=3):
    """Query the knowledge base with a text query"""
    print(f"Querying knowledge base with: '{query_text}'")

    # Generate embedding for the query
    query_embedding = get_openai_embedding(query_text)

    # Query the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results


def get_rag_response(query_text, n_results=3):
    """Process a query and return formatted RAG results as a string"""
    # Load documents from markdown files
    documents = load_markdown_files()
    
    # Initialize ChromaDB with the documents
    collection = initialize_chroma_db(documents)
    
    # Query the knowledge base
    results = query_knowledge_base(collection, query_text, n_results)
    
    # Format results as a string
    response_parts = [f"📚 Results for: '{query_text}'"]
    
    if results["documents"][0]:
        for idx, (doc, meta, dist) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0])):
                
            # Limit document preview for response
            doc_preview = doc[:500] + "..." if len(doc) > 500 else doc
            
            response_parts.append(f"\n📑 Source {idx+1}: {meta['title']}")
            response_parts.append(f"🔍 Relevance: {1 - dist:.2f}")
            response_parts.append(f"📖 Content: {doc_preview}\n")
    else:
        response_parts.append("❌ No relevant documents found for your query.")
        
    return "\n".join(response_parts)


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Query the knowledge base with a custom question')
    parser.add_argument('--query', type=str, default="Tell me about Dendrochronology", 
                        help='The query to search for in the knowledge base')
    args = parser.parse_args()
    
    # Get and print response using the function
    response = get_rag_response(args.query)
    print(response)


if __name__ == "__main__":
    main()

