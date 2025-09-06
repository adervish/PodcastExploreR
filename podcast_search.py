#!/usr/bin/env python3
import sqlite3
import os
import shutil
import urllib.parse
from pathlib import Path

class PodcastSearcher:
    def __init__(self, db_path):
        self.db_path = db_path
        self.downloads_dir = Path.home() / "Downloads"
        
    def search_podcasts(self, search_term):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT ZTITLE, ZASSETURL, ZPUBDATE, ZAUTHOR, ZDURATION
        FROM ZMTEPISODE 
        WHERE ZTITLE LIKE ? AND ZASSETURL LIKE 'file://%'
        ORDER BY ZPUBDATE DESC
        """
        
        cursor.execute(query, (f'%{search_term}%',))
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def display_results(self, results):
        if not results:
            print("No matching podcasts found.")
            return None
            
        print(f"\nFound {len(results)} matching podcasts:")
        print("-" * 80)
        
        for i, (title, asset_url, pub_date, author, duration) in enumerate(results, 1):
            duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}" if duration else "Unknown"
            print(f"{i:2d}. {title}")
            print(f"    Author: {author or 'Unknown'}")
            print(f"    Duration: {duration_str}")
            if pub_date:
                import datetime
                pub_datetime = datetime.datetime.fromtimestamp(pub_date + 978307200)  # Core Data epoch offset
                print(f"    Published: {pub_datetime.strftime('%Y-%m-%d %H:%M')}")
            print()
            
        return results
    
    def copy_podcast(self, asset_url, title):
        file_url = urllib.parse.unquote(asset_url)
        source_path = file_url.replace('file://', '')
        
        if not os.path.exists(source_path):
            print(f"Source file not found: {source_path}")
            return False
            
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        
        file_extension = Path(source_path).suffix
        dest_filename = f"{safe_title}{file_extension}"
        dest_path = self.downloads_dir / dest_filename
        
        counter = 1
        while dest_path.exists():
            dest_filename = f"{safe_title}_{counter}{file_extension}"
            dest_path = self.downloads_dir / dest_filename
            counter += 1
            
        try:
            shutil.copy2(source_path, dest_path)
            print(f"Successfully copied to: {dest_path}")
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False

def main():
    db_path = "/Users/acd/Library/Group Containers/243LU875E5.groups.com.apple.podcasts/Documents/MTLibrary.sqlite"
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
        
    searcher = PodcastSearcher(db_path)
    
    while True:
        search_term = input("\nEnter search term (or 'quit' to exit): ").strip()
        
        if search_term.lower() == 'quit':
            print("Goodbye!")
            break
            
        if not search_term:
            print("Please enter a search term.")
            continue
            
        results = searcher.search_podcasts(search_term)
        displayed_results = searcher.display_results(results)
        
        if not displayed_results:
            continue
            
        while True:
            try:
                choice = input(f"Select podcast (1-{len(displayed_results)}) or 'back' for new search: ").strip()
                
                if choice.lower() == 'back':
                    break
                    
                choice_num = int(choice)
                if 1 <= choice_num <= len(displayed_results):
                    selected = displayed_results[choice_num - 1]
                    title, asset_url = selected[0], selected[1]
                    
                    print(f"\nSelected: {title}")
                    confirm = input("Copy this podcast to ~/Downloads? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        searcher.copy_podcast(asset_url, title)
                    break
                else:
                    print(f"Please enter a number between 1 and {len(displayed_results)}")
                    
            except ValueError:
                print("Please enter a valid number or 'back'")
            except KeyboardInterrupt:
                print("\nExiting...")
                return

if __name__ == "__main__":
    main()