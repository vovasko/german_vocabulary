# Vocabulary Booster

A Python-based application for translating and managing German vocabulary words. This app uses various libraries to fetch, translate, and store words, providing a user-friendly interface for language learners.
Check out [new version](https://github.com/vovasko/vocabulary-v2) of the app!

## Features

- Translate individual words or batches of words
- Fetch word information from Netzverb
- Learn words with flashcards and point system
- Store and manage vocabulary in a SQLite Database
- Display vocabulary with filters for nouns, verbs, adjectives, and other types
- Identify and manage duplicate entries
- Edit/Delete records 

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/vovasko/german_vocabulary
    ```
2. Navigate to the project directory:
    ```sh
    cd german-vocabulary
    ```
3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
4. Download the SpaCy language model:
    ```sh
    python -m spacy download de_core_news_sm
    ```

## Usage

1. Run the application:
    ```sh
    python main.py
    ```
2. Use the GUI to input words, translate them, and manage your vocabulary.

## Project Structure

- `main.py`: The main application file containing the GUI and core functionality.
- `vocabulary.py`: Contains classes and methods for fetching information from Netzverb.
- `DB_manager.py`: Contains class for managing SQLite Database
- `requirements.txt`: Lists the dependencies required for the project.

## Dependencies

- `requests`: For making HTTP requests to fetch word information.
- `beautifulsoup4`: For parsing HTML content.
- `pandas`: For managing and manipulating data.
- `spacy`: For natural language processing tasks.
- `textwrap`: For formatting text.
- `pathlib`: For handling file paths.
- `tkinter`: For creating the GUI.
- `customtkinter`: For enhanced GUI components.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.