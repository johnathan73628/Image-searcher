#!/usr/bin/env python3
"""
Image Similarity Finder
Scrapes a website for images and finds matches to a reference image
"""

import os
import sys
import argparse
import requests
from urllib.parse import urljoin, urlparse
from PIL import Image
import imagehash
from io import BytesIO
from bs4 import BeautifulSoup
import time
import json


class ImageFinder:
    def __init__(self, start_url, reference_image_path, similarity_threshold=10):
        self.start_url = start_url
        self.reference_image_path = reference_image_path
        self.similarity_threshold = similarity_threshold
        self.visited_urls = set()
        self.image_matches = []
        self.reference_hash = None
        self.total_images_found = 0
        self.total_images_checked = 0

    def load_reference_image(self):
        try:
            ref_img = Image.open(self.reference_image_path)
            self.reference_hash = imagehash.phash(ref_img)
            print(f"Reference image loaded: {self.reference_image_path}")
            print(f"Hash: {self.reference_hash}")
            print(f"Size: {ref_img.size}\n")
        except Exception as e:
            print(f"Error loading reference image: {e}")
            sys.exit(1)

    def get_page_content(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def get_element_selector(self, element):
        if element.get('id'):
            return f"#{element.get('id')}"

        path_parts = []
        current = element
        depth = 0

        while current and current.name and depth < 5:
            tag = current.name
            if current.get('id'):
                path_parts.insert(0, f"{tag}#{current.get('id')}")
                break
            elif current.get('class'):
                classes = '.'.join(current.get('class'))
                path_parts.insert(0, f"{tag}.{classes}")
            else:
                path_parts.insert(0, tag)

            current = current.parent
            depth += 1

        return ' > '.join(path_parts) if path_parts else 'Unknown'

    def get_surrounding_context(self, img_element):
        context = []
        parent = img_element.parent

        if parent:
            if parent.name == 'figure':
                caption = parent.find('figcaption')
                if caption:
                    context.append(f"Figure: {caption.get_text(strip=True)[:100]}")

            nearby_text = parent.get_text(strip=True)[:200]
            if nearby_text:
                context.append(f"Nearby: {nearby_text}")

        return ' | '.join(context) if context else 'No context'

    def extract_images_and_links(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')

        images = []
        for img in soup.find_all('img'):
            img_url = img.get('src') or img.get('data-src')
            if img_url:
                full_url = urljoin(url, img_url)

                images.append({
                    'url': full_url,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'css_selector': self.get_element_selector(img),
                    'context': self.get_surrounding_context(img)
                })

        links = []
        for link in soup.find_all('a', href=True):
            full_link = urljoin(url, link['href'])
            if self.same_domain(full_link, self.start_url):
                links.append(full_link)

        return images, links

    def same_domain(self, url1, url2):
        return urlparse(url1).netloc == urlparse(url2).netloc

    def download_and_hash_image(self, img_url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(img_url, headers=headers, timeout=10)
            response.raise_for_status()

            if 'image' not in response.headers.get('content-type', ''):
                return None, None, None

            img = Image.open(BytesIO(response.content))
            img_hash = imagehash.phash(img)

            return img_hash, img.size, response.content

        except Exception:
            return None, None, None

    def save_matched_image(self, image_content, match_number):
        output_dir = "matched_images"
        os.makedirs(output_dir, exist_ok=True)

        filename = f"{output_dir}/match_{match_number}.jpg"

        try:
            img = Image.open(BytesIO(image_content))
            img.save(filename)
            return filename
        except:
            return None

    def find_similar_images(self, url, images):
        self.total_images_found += len(images)

        for idx, img_data in enumerate(images, 1):
            img_hash, img_size, img_content = self.download_and_hash_image(img_data['url'])

            if img_hash:
                self.total_images_checked += 1
                diff = self.reference_hash - img_hash

                if diff <= self.similarity_threshold:
                    print(f"Match found! Score: {diff} -> {img_data['url']}")

                    self.image_matches.append({
                        'image_url': img_data['url'],
                        'page_url': url,
                        'similarity': diff,
                        'alt': img_data['alt'],
                        'context': img_data['context'],
                        'size': img_size,
                        'css_selector': img_data['css_selector'],
                        'content': img_content
                    })

            time.sleep(0.2)

    def crawl(self, url, max_depth=2, depth=0):
        if depth > max_depth or url in self.visited_urls:
            return

        print(f"[Depth {depth}] {url}")
        self.visited_urls.add(url)

        html = self.get_page_content(url)
        if not html:
            return

        images, links = self.extract_images_and_links(url, html)
        print(f"Found {len(images)} images")

        self.find_similar_images(url, images)

        for link in links[:5]:
            time.sleep(0.5)
            self.crawl(link, max_depth, depth + 1)

    def display_results(self):
        print("\n=== RESULTS ===")
        print(f"Pages visited: {len(self.visited_urls)}")
        print(f"Images checked: {self.total_images_checked}")
        print(f"Matches: {len(self.image_matches)}\n")

        for i, match in enumerate(sorted(self.image_matches, key=lambda x: x['similarity']), 1):
            saved = self.save_matched_image(match['content'], i)

            print(f"\nMatch #{i}")
            print(f"Similarity: {match['similarity']}")
            print(f"Image: {match['image_url']}")
            print(f"Page: {match['page_url']}")
            print(f"Saved: {saved}")
            print(f"Selector: {match['css_selector']}")
            print(f"Context: {match['context']}")
            print(f"Size: {match['size']}")

    def run(self, depth):
        self.load_reference_image()
        self.crawl(self.start_url, depth)
        self.display_results()


def main():
    parser = argparse.ArgumentParser(description="Find similar images on a website")

    parser.add_argument("url", help="Website URL")
    parser.add_argument("image", help="Reference image path")
    parser.add_argument("--threshold", type=int, default=10)
    parser.add_argument("--depth", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.image):
        print("Image not found!")
        sys.exit(1)

    finder = ImageFinder(args.url, args.image, args.threshold)
    finder.run(args.depth)


if __name__ == "__main__":
    main()
    
