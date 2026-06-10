# Imperative to Functional Code Transformer

## Overview

This project is a source-to-source code transformation tool that converts imperative Python code into a functional programming style.

The system analyzes Python code through multiple stages:

1. Abstract Syntax Tree (AST) Generation
2. Control Flow Graph (CFG) Construction
3. Static Single Assignment (SSA) Conversion
4. Functional Code Generation

A web-based interface allows users to visualize and interact with the transformation process.

---

## Features

* Parse Python source code into an AST
* Build Control Flow Graphs (CFG)
* Convert code into Static Single Assignment (SSA) form
* Generate functional-style Python code
* Interactive React frontend
* Flask backend API
* Modular and extensible architecture

---

## Architecture

```text
User Input
     |
     v
+------------+
|   Parser   |
|    AST     |
+------------+
     |
     v
+------------+
|    CFG     |
| Generation |
+------------+
     |
     v
+------------+
|    SSA     |
| Conversion |
+------------+
     |
     v
+------------+
|  Emitter   |
| Functional |
|    Code    |
+------------+
     |
     v
 Transformed Output
```

---

## Technology Stack

### Backend

* Python
* Flask
* Python AST Module

### Frontend

* React
* Vite
* JavaScript
* Tailwind CSS

### Concepts Used

* Compiler Design
* Abstract Syntax Trees (AST)
* Control Flow Graphs (CFG)
* Static Single Assignment (SSA)
* Functional Programming

---

## Project Structure

```text
imperative-to-functional/

├── app.py
├── README.md
├── .gitignore

├── project/
│   ├── parser.py
│   ├── cfg.py
│   ├── ssa.py
│   ├── emitter.py
│   └── main.py

├── tests/
│   ├── __init__.py
│   └── test_cases.py

└── transformer-ui/
    ├── src/
    ├── public/
    ├── package.json
    └── vite.config.js
```

---

## Running the Backend

```bash
pip install flask flask-cors
python app.py
```

Backend will start at:

```text
http://127.0.0.1:5000
```

---

## Running the Frontend

```bash
cd transformer-ui
npm install
npm run dev
```

Frontend will start at:

```text
http://localhost:5173
```

---

## Example Transformation

### Imperative Code

```python
result = []
for x in items:
    result.append(x * 2)
```

### Functional Style

```python
result = list(map(lambda x: x * 2, items))
```

---

## Future Enhancements

* Automatic transformation using `map()`
* Automatic transformation using `filter()`
* Automatic transformation using `reduce()`
* Enhanced CFG visualization
* Interactive SSA visualization
* Support for more complex control structures

---

## Author

**Dhakshanamoorthy Karthikeyan**

Master's Student in Computer Science

VSB – Technical University of Ostrava
