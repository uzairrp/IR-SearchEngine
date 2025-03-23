# 🔎 Search Engine with Web Analytics  
### 📚 Information Retrieval Project

This project contains the code for processing raw, real-world text data and preparing it for a **search engine**. It also includes the initial **Flask setup** for a simple web application interface.

The Jupyter Notebook is divided into **three main parts**, each handling a different stage of textual data processing — from cleaning to indexing and ranking.

---

## 📊 Analysis

This section focuses on processing raw text data. It involves:

- 📂 Reading text files from a specified directory  
- 🧹 Cleaning and tokenizing the text  
- 🏷️ Extracting metadata (such as titles or headings)  
- 🧠 Performing Named Entity Recognition (NER) / keyword extraction  

---

## 🧱 Indexing

Here we prepare the cleaned data for efficient retrieval:

- 🔁 Convert cleaned text into index structures  
- 📈 Use TF-IDF or other vector-based models  
- 📇 Create an inverted index or document-term matrix  

---

## 📈 Ranking

In this final stage:

- 🔍 Accept a search query or keyword input  
- 🧮 Compute similarity scores with indexed documents  
- 📊 Rank documents based on relevance  
- 📃 Display top-ranked documents with scores or matched highlights  

---

## ⚙️ How to Run

Make sure your **input text files** are located in the directory defined early in the notebook. The notebook may generate or expect the following outputs:

- ✨ Cleaned text/token files  
- 📁 Index files (`.pkl`, `.json`, etc.)  
- 📝 Ranking results (printed or saved)  

✅ It’s recommended to ensure all output paths/directories exist before running.

📦 To install required packages, use `pip` as needed.

💡 **Pro Tip:**  
The notebook is **modular** — each part can be run independently if data dependencies are met.  
However, it’s a good idea to **run all cells in order** once to initialize everything properly.

---

## Starting the Web App

```bash
python -V
# Make sure we use Python 3

cd search-engine-web-app
python web_app.py
```
The above will start a web server with the application:
```
 * Serving Flask app 'web-app' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8088/ (Press CTRL+C to quit)
```

Open Web app in your Browser:  
[http://127.0.0.1:8088/](http://127.0.0.1:8088/) or [http://localhost:8088/](http://localhost:8088/)


## Virtualenv for the project (first time use)
### Install virtualenv
Having different version of libraries for different projects.  
Solves the elevated privilege issue as virtualenv allows you to install with user permission.

In the project root directory execute:
```bash
pip3 install virtualenv
virtualenv --version
```
virtualenv 20.10.0

### Prepare virtualenv for the project
In the root of the project folder run:
```bash
virtualenv .
```

If you list the contents of the project root directory, you will see that it has created several sub-directories, including a bin folder (Scripts on Windows) that contains copies of both Python and pip. Also, a lib folder will be created by this action.

The next step is to activate your new virtualenv for the project:

```bash
source bin/activate
```

or for Windows...
```cmd
myvenv\Scripts\activate.bat
```

This will load the python virtualenv for the project.

### Installing Flask and other packages in your virtualenv
```bash
pip install Flask pandas nltk faker
```

Enjoy!




## Git Help
After creating the project and code in local computer...

1. Login to GitHub and create a new repo.
2. Go to the root page of your new repo and note the url from the browser.
3. Execute the following locally.
4. 
```bash
cd <project root folder>
git init -b main
git add . && git commit -m "initial commit"
git remote add origin <your GitHub repo URL from the browser>
git push -u origin main
```




