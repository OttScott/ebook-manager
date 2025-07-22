#!/usr/bin/env python3
"""
Test script to verify Calibre database access and integration.
"""
import subprocess
import json
import os
import sys

def find_calibredb():
    """Find calibredb executable."""
    common_paths = [
        r"E:\Program Files\Calibre2\calibredb.exe",
        r"C:\Program Files\Calibre2\calibredb.exe", 
        r"C:\Program Files (x86)\Calibre2\calibredb.exe",
        "calibredb.exe",
        "calibredb"
    ]
    
    for path in common_paths:
        if os.path.exists(path) if path.endswith('.exe') else True:
            try:
                # Test if it works
                result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print(f"✓ Found calibredb at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
    
    print("❌ Could not find calibredb")
    return None

def test_calibre_database_access():
    """Test basic access to Calibre database."""
    print("🔍 Testing Calibre Database Access")
    print("=" * 50)
    
    calibredb = find_calibredb()
    if not calibredb:
        return False
    
    # Test basic list command
    print("\n1. Testing basic list command...")
    try:
        result = subprocess.run(
            [calibredb, "list", "--limit", "5"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Basic list command works")
            print("Sample output:")
            for line in result.stdout.strip().split('\n')[:5]:
                print(f"  {line}")
        else:
            print(f"❌ Basic list failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out - Calibre might be locked")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test JSON format
    print("\n2. Testing JSON format...")
    try:
        result = subprocess.run(
            [calibredb, "list", "--for-machine", "--limit", "3"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                books = json.loads(result.stdout)
                print(f"✓ JSON format works - found {len(books)} books")
                if books:
                    print("Sample book:")
                    book = books[0]
                    print(f"  ID: {book.get('id')}")
                    print(f"  Title: {book.get('title')}")
                    print(f"  Authors: {book.get('authors')}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw output: {result.stdout[:200]}...")
                return False
        else:
            print(f"❌ JSON list failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_calibre_library_location():
    """Test getting Calibre library location."""
    print("\n3. Testing library location...")
    calibredb = find_calibredb()
    if not calibredb:
        return None
    
    try:
        # Try to get library path
        result = subprocess.run(
            [calibredb, "list", "--limit", "1"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse output to extract library path
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('id'):
                    print(f"✓ Library accessible")
                    break
        else:
            print(f"❌ Could not access library: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error getting library location: {e}")

def test_file_paths():
    """Test getting actual file paths from Calibre."""
    print("\n4. Testing file path extraction...")
    calibredb = find_calibredb()
    if not calibredb:
        return
    
    try:
        # Get a book with file paths
        result = subprocess.run(
            [calibredb, "list", "--fields", "id,title,path", "--limit", "3", "--for-machine"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            books = json.loads(result.stdout)
            print(f"✓ Got {len(books)} books with path information")
            
            for book in books:
                book_id = book.get('id')
                title = book.get('title')
                path = book.get('path')
                print(f"  Book {book_id}: {title}")
                print(f"    Path: {path}")
                
                # Try to get actual file paths
                try:
                    path_result = subprocess.run(
                        [calibredb, "list_paths", str(book_id)],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if path_result.returncode == 0:
                        file_paths = [line.strip() for line in path_result.stdout.strip().split('\n') if line.strip()]
                        print(f"    Files: {len(file_paths)}")
                        for fp in file_paths:
                            exists = "✓" if os.path.exists(fp) else "❌"
                            print(f"      {exists} {fp}")
                    else:
                        print(f"    ❌ Could not get file paths: {path_result.stderr}")
                        
                except Exception as e:
                    print(f"    ❌ Error getting file paths: {e}")
                    
        else:
            print(f"❌ Could not get books with paths: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error testing file paths: {e}")

def main():
    """Run all tests."""
    print("🧪 CALIBRE DATABASE INTEGRATION TEST")
    print("=" * 60)
    
    success = test_calibre_database_access()
    test_calibre_library_location()
    test_file_paths()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ CALIBRE DATABASE ACCESS WORKING!")
        print("The integration should work correctly.")
    else:
        print("❌ CALIBRE DATABASE ACCESS ISSUES DETECTED")
        print("Please close Calibre application and try again.")
    print("=" * 60)

if __name__ == "__main__":
    main()
