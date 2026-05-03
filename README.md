# Image Similarity Finder

A Python CLI tool that crawls a website, extracts images, and identifies ones that are visually similar to a reference image using perceptual hashing.

---

## 📌 What this project does

**Image Similarity Finder** is a web scraping and image comparison tool that:

* Crawls a target website starting from a given URL
* Extracts all images from pages within the same domain
* Compares each image to a reference image using perceptual hashing (pHash)
* Identifies visually similar images based on a configurable threshold
* Saves matched images locally with contextual metadata (page location, HTML context, CSS selector)

---

## 🚀 Why this project is useful

This tool is helpful for:

* Detecting reused or duplicated images across a website
* Finding visually similar content for auditing or research
* Monitoring image reuse across pages (content tracking)
* Assisting in OSINT-style investigations
* Building datasets of similar visual assets

### ✨ Key features

* 🔍 **Website crawler with depth control**
* 🧠 **Perceptual image hashing (imagehash pHash)**
* 🌐 **Domain-restricted crawling**
* 🧾 **Rich image metadata extraction (alt text, context, CSS path)**
* 📁 **Automatic saving of matched images**
* ⚙️ **Configurable similarity threshold**
* 🧭 **Lightweight CLI interface**

---

# Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/image-similarity-finder.git
cd image-similarity-finder
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install requests pillow imagehash beautifulsoup4
```

---

##  Usage

### Basic command

```bash
python image_finder.py <url> <reference_image>
```

### Example

```bash
python image_finder.py https://example.com ./reference.jpg
```

---

##  Options

| Flag          | Description                                   | Default |
| ------------- | --------------------------------------------- | ------- |
| `--threshold` | Similarity threshold (lower = stricter match) | 10      |
| `--depth`     | Crawl depth for website traversal             | 2       |

### Example with options

```bash
python image_finder.py https://example.com reference.jpg --threshold 8 --depth 3
```

---

## Output

Matched images are saved in:

```
matched_images/
```

Each file is stored as:

```
match_1.jpg
match_2.jpg
```

The CLI also prints:

* Similarity score
* Source image URL
* Page URL
* CSS selector path
* Surrounding HTML/text context
* Image dimensions



##  How it works

1. Loads a reference image and computes its perceptual hash
2. Crawls pages within the same domain up to a defined depth
3. Extracts all `<img>` elements from HTML
4. Downloads and hashes each image
5. Compares hashes using Hamming distance
6. Flags images under the similarity threshold as matches


##  Dependencies

* `requests` – HTTP requests
* `Pillow` – Image processing
* `imagehash` – Perceptual hashing
* `beautifulsoup4` – HTML parsing

## Contributing

Contributions are welcome.

To contribute:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request


