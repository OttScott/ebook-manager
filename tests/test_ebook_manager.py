import os
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Import the ebook_manager package
import ebook_manager

# Import functions from __main__ module
from ebook_manager.__main__ import (
    BEETS_EXE,
    batch_import_ebooks,
    import_collection,
    import_collection_dual,
    import_ebook_to_beets,
    import_ebook_to_calibre,
    process_ebook_with_beets,
    scan_collection,
    scan_collection_calibre,
    import_from_calibre_database,
    bidirectional_sync_workflow,
    reverse_sync_workflow,
)
from ebook_manager.core import (
    FORMAT_PRIORITY,
    extract_book_identifier,
    filter_onefile_per_book,
    find_books_in_calibre,
    find_calibredb,
    find_ebooks,
    import_to_calibre,
    is_ebook_file,
    parse_extensions,
    sync_calibre_after_move,
    sync_calibre_with_beets_library,
    update_calibre_book_path,
    get_all_calibre_books,
    import_calibre_database_to_beets,
    reverse_calibre_sync,
    bidirectional_calibre_sync,
)


class TestEbookManager(unittest.TestCase):
    """Test cases for the ebook_manager.py functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = []

        # Create test ebook files with various extensions
        test_books = [
            "J.R.R. Tolkien - The Lord of the Rings.epub",
            "Isaac Asimov - Foundation.pdf",
            "Douglas Adams - Hitchhiker's Guide.mobi",
            "Terry Pratchett - Discworld.azw",
            "Ursula K. Le Guin - Left Hand of Darkness.azw3",
            "Frank Herbert - Dune.lrf",
            "Ray Bradbury - Fahrenheit 451.txt",  # Not an ebook
            "Arthur C. Clarke - 2001.mp3",  # Not an ebook
        ]

        for book in test_books:
            file_path = os.path.join(self.test_dir, book)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Test content for {book}")
            self.test_files.append(file_path)

    def tearDown(self):
        """Clean up test fixtures."""
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.unlink(file_path)
        os.rmdir(self.test_dir)

    def test_is_ebook_file_basic(self):
        """Test basic ebook file detection."""
        test_cases = [
            ("book.epub", True),
            ("document.pdf", True),
            ("story.mobi", True),
            ("novel.azw", True),
            ("book.azw3", True),
            ("file.lrf", True),
            ("music.mp3", False),
            ("image.jpg", False),
            ("text.txt", False),
        ]

        for filename, expected in test_cases:
            with self.subTest(filename=filename):
                result = is_ebook_file(filename)
                self.assertEqual(result, expected, f"Failed for {filename}")

    def test_is_ebook_file_with_allowed_extensions(self):
        """Test ebook file detection with custom allowed extensions."""
        # Test with only EPUB allowed
        epub_only = [".epub"]
        self.assertTrue(is_ebook_file("book.epub", epub_only))
        self.assertFalse(is_ebook_file("book.pdf", epub_only))
        self.assertFalse(is_ebook_file("book.mobi", epub_only))

        # Test with EPUB and PDF allowed
        epub_pdf = [".epub", ".pdf"]
        self.assertTrue(is_ebook_file("book.epub", epub_pdf))
        self.assertTrue(is_ebook_file("book.pdf", epub_pdf))
        self.assertFalse(is_ebook_file("book.mobi", epub_pdf))

        # Test case insensitivity
        self.assertTrue(is_ebook_file("BOOK.EPUB", epub_only))
        self.assertTrue(is_ebook_file("Book.Epub", epub_only))

    def test_find_ebooks_all_types(self):
        """Test finding all ebook types in directory."""
        ebooks = find_ebooks(self.test_dir)

        # Should find 6 ebook files (excluding .txt and .mp3)
        self.assertEqual(len(ebooks), 6)

        # Check that all ebook files are found
        ebook_basenames = [os.path.basename(f) for f in ebooks]
        expected_ebooks = [
            "J.R.R. Tolkien - The Lord of the Rings.epub",
            "Isaac Asimov - Foundation.pdf",
            "Douglas Adams - Hitchhiker's Guide.mobi",
            "Terry Pratchett - Discworld.azw",
            "Ursula K. Le Guin - Left Hand of Darkness.azw3",
            "Frank Herbert - Dune.lrf",
        ]

        for expected in expected_ebooks:
            self.assertIn(expected, ebook_basenames)

        # Should not include non-ebook files
        self.assertNotIn("Ray Bradbury - Fahrenheit 451.txt", ebook_basenames)
        self.assertNotIn("Arthur C. Clarke - 2001.mp3", ebook_basenames)

    def test_find_ebooks_with_filtering(self):
        """Test finding ebooks with extension filtering."""
        # Test EPUB only
        epub_files = find_ebooks(self.test_dir, [".epub"])
        self.assertEqual(len(epub_files), 1)
        self.assertTrue(epub_files[0].endswith(".epub"))

        # Test PDF only
        pdf_files = find_ebooks(self.test_dir, [".pdf"])
        self.assertEqual(len(pdf_files), 1)
        self.assertTrue(pdf_files[0].endswith(".pdf"))

        # Test EPUB and PDF
        epub_pdf_files = find_ebooks(self.test_dir, [".epub", ".pdf"])
        self.assertEqual(len(epub_pdf_files), 2)
        extensions = [os.path.splitext(f)[1].lower() for f in epub_pdf_files]
        self.assertIn(".epub", extensions)
        self.assertIn(".pdf", extensions)

        # Test with non-existent extension
        no_files = find_ebooks(self.test_dir, [".xyz"])
        self.assertEqual(len(no_files), 0)

    def test_parse_extensions(self):
        """Test extension parsing functionality."""
        # Test None input
        result = parse_extensions(None)
        self.assertIsNone(result)

        # Test empty string
        result = parse_extensions("")
        self.assertIsNone(result)

        # Test single extension with dot
        result = parse_extensions(".epub")
        self.assertEqual(result, [".epub"])

        # Test single extension without dot
        result = parse_extensions("epub")
        self.assertEqual(result, [".epub"])

        # Test multiple extensions with dots
        result = parse_extensions(".epub,.pdf,.mobi")
        self.assertEqual(result, [".epub", ".pdf", ".mobi"])

        # Test multiple extensions without dots
        result = parse_extensions("epub,pdf,mobi")
        self.assertEqual(result, [".epub", ".pdf", ".mobi"])

        # Test mixed case
        result = parse_extensions(".EPUB,.PDF")
        self.assertEqual(result, [".epub", ".pdf"])

        # Test with spaces
        result = parse_extensions(" .epub , .pdf , .mobi ")
        self.assertEqual(result, [".epub", ".pdf", ".mobi"])

    @patch("subprocess.run")
    def test_process_ebook_with_beets_success(self, mock_run):
        """Test successful ebook processing with beets."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Processing successful"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = process_ebook_with_beets("test.epub")

        self.assertEqual(result, "Processing successful")
        mock_run.assert_called_once_with(
            [BEETS_EXE, "ebook", "test.epub"],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_process_ebook_with_beets_error(self, mock_run):
        """Test ebook processing error handling."""
        # Mock subprocess error
        mock_run.side_effect = subprocess.CalledProcessError(1, "beet")

        with patch("builtins.print") as mock_print:
            result = process_ebook_with_beets("test.epub")

        self.assertIsNone(result)
        mock_print.assert_called()

    @patch("subprocess.run")
    def test_import_ebook_to_beets_success(self, mock_run):
        """Test successful ebook import to beets."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Successfully imported ebook"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = import_ebook_to_beets("test.epub")

        self.assertEqual(result, "Successfully imported ebook")
        # Should use absolute path
        expected_path = os.path.abspath("test.epub")
        mock_run.assert_called_once_with(
            [BEETS_EXE, "import-ebooks", expected_path],
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.print")
    def test_scan_collection_with_filtering(self, mock_print, mock_find):
        """Test collection scanning with extension filtering."""
        # Mock finding 2 EPUB files
        mock_find.return_value = ["book1.epub", "book2.epub"]

        with patch(
            "ebook_manager.__main__.process_ebook_with_beets"
        ) as mock_process:
            mock_process.return_value = "Processed successfully"
            scan_collection(self.test_dir, [".epub"])

        # Check that find_ebooks was called with filtering
        mock_find.assert_called_once_with(self.test_dir, [".epub"])

        # Check that filtering message was printed
        print_calls = [
            call_obj.args[0] for call_obj in mock_print.call_args_list
        ]
        self.assertTrue(
            any(
                "Filtering by extensions: [" in call_text
                for call_text in print_calls
            )
        )

    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_import_collection_with_filtering(
        self, mock_print, mock_input, mock_find
    ):
        """Test collection import with extension filtering."""
        # Mock user input and found files
        mock_input.return_value = "y"
        mock_find.return_value = ["book1.epub", "book2.epub"]

        with patch(
            "ebook_manager.__main__.import_ebook_to_beets"
        ) as mock_import:
            mock_import.return_value = "Successfully imported ebook"
            import_collection(self.test_dir, [".epub"])

        # Check that find_ebooks was called with filtering
        mock_find.assert_called_once_with(self.test_dir, [".epub"])

        # Check that import was called for each file
        self.assertEqual(mock_import.call_count, 2)

    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.input")
    @patch("subprocess.run")
    def test_batch_import_with_filtering(
        self, mock_run, mock_input, mock_find
    ):
        """Test batch import with extension filtering uses individual imports."""
        # Mock user input and found files
        mock_input.return_value = "y"
        mock_find.return_value = ["book1.epub", "book2.epub"]

        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Successfully imported ebook"
        mock_run.return_value = mock_result

        with patch("builtins.print"):
            batch_import_ebooks(self.test_dir, [".epub"])

        # When filtering, should use individual imports (2 calls)
        self.assertEqual(mock_run.call_count, 2)

        # Check that each call uses import-ebooks with individual files
        for call_obj in mock_run.call_args_list:
            args = call_obj[0][0]  # Get the command arguments
            self.assertEqual(args[1], "import-ebooks")
            self.assertTrue(args[2].endswith(".epub"))

    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.input")
    @patch("subprocess.run")
    def test_batch_import_without_filtering(
        self, mock_run, mock_input, mock_find
    ):
        """Test batch import without filtering uses directory import."""
        # Mock user input and found files
        mock_input.return_value = "y"
        mock_find.return_value = ["book1.epub", "book2.pdf"]

        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.stdout = "Batch import successful"
        mock_run.return_value = mock_result

        with patch("builtins.print"):
            batch_import_ebooks(self.test_dir, None)

        # When not filtering, should use directory import (1 call)
        self.assertEqual(mock_run.call_count, 1)

        # Check that it uses the directory path
        args = mock_run.call_args[0][0]
        self.assertEqual(args[1], "import-ebooks")
        self.assertEqual(args[2], os.path.abspath(self.test_dir))

    def test_extension_filtering_integration(self):
        """Integration test for extension filtering across all functions."""
        # Test that all functions correctly use extension filtering

        # Test with EPUB only
        epub_files = find_ebooks(self.test_dir, [".epub"])
        self.assertEqual(len(epub_files), 1)
        self.assertTrue(all(f.endswith(".epub") for f in epub_files))

        # Test with multiple extensions
        multi_files = find_ebooks(self.test_dir, [".epub", ".pdf", ".mobi"])
        self.assertEqual(len(multi_files), 3)

        # Test that filtering affects different functions consistently
        for allowed_ext in [[".epub"], [".pdf"], [".epub", ".pdf"]]:
            files_found = find_ebooks(self.test_dir, allowed_ext)

            # All found files should match the allowed extensions
            for file_path in files_found:
                file_ext = os.path.splitext(file_path)[1].lower()
                self.assertIn(file_ext, allowed_ext)

    def test_case_insensitive_extension_matching(self):
        """Test that extension matching is case insensitive."""
        # Create test files with mixed case extensions
        mixed_case_dir = tempfile.mkdtemp()
        mixed_files = []

        try:
            test_books = [
                "book1.EPUB",
                "book2.Pdf",
                "book3.MoBi",
            ]

            for book in test_books:
                file_path = os.path.join(mixed_case_dir, book)
                with open(file_path, "w") as f:
                    f.write(f"Test content for {book}")
                mixed_files.append(file_path)

            # Test that lowercase filter matches uppercase files
            epub_files = find_ebooks(mixed_case_dir, [".epub"])
            self.assertEqual(len(epub_files), 1)
            self.assertTrue(epub_files[0].endswith(".EPUB"))

            # Test that mixed case filters work (input gets normalized)
            # Using mixed case input that gets normalized to lowercase
            mixed_case_extensions = parse_extensions(".EPUB,.Pdf,.MoBi")
            all_files = find_ebooks(mixed_case_dir, mixed_case_extensions)
            self.assertEqual(len(all_files), 3)

        finally:
            for file_path in mixed_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            os.rmdir(mixed_case_dir)

    def test_extract_book_identifier(self):
        """Test extracting book identifiers for grouping."""
        test_cases = [
            (
                "Douglas Adams - The Hitchhiker's Guide to the Galaxy.epub",
                "douglas adams - the hitchhiker's guide to the galaxy",
            ),
            (
                "J.R.R. Tolkien - The Lord of the Rings (1).pdf",
                "j.r.r. tolkien - the lord of the rings",
            ),
            (
                "Isaac Asimov - Foundation [2005].mobi",
                "isaac asimov - foundation",
            ),
            ("Terry Pratchett - Discworld.azw", "terry pratchett - discworld"),
            ("single_word_title.epub", "single_word_title"),  # Fallback case
        ]

        for filepath, expected in test_cases:
            with self.subTest(filepath=filepath):
                result = extract_book_identifier(filepath)
                self.assertEqual(result, expected)

    def test_filter_onefile_per_book(self):
        """Test filtering to keep only one file per book."""
        # Create test files for duplicate books
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        try:
            test_files = [
                "Douglas Adams - The Hitchhiker's Guide to the Galaxy.epub",
                "Douglas Adams - The Hitchhiker's Guide to the Galaxy.mobi",
                "Douglas Adams - The Hitchhiker's Guide to the Galaxy.pdf",
                "Isaac Asimov - Foundation.pdf",
                "J.R.R. Tolkien - The Lord of the Rings.epub",
                "J.R.R. Tolkien - The Lord of the Rings.mobi",
            ]

            for filename in test_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, "w") as f:
                    f.write(f"Content for {filename}")
                file_paths.append(filepath)

            # Test filtering
            filtered = filter_onefile_per_book(file_paths)

            # Should keep only highest priority format per book
            filtered_names = [os.path.basename(f) for f in filtered]

            # Expected: epub (highest) for duplicates, pdf for Foundation (only one)
            expected_names = [
                "Douglas Adams - The Hitchhiker's Guide to the Galaxy.epub",
                "Isaac Asimov - Foundation.pdf",
                "J.R.R. Tolkien - The Lord of the Rings.epub",
            ]

            self.assertEqual(len(filtered), 3)
            for expected in expected_names:
                self.assertIn(expected, filtered_names)

        finally:
            # Cleanup
            for filepath in file_paths:
                if os.path.exists(filepath):
                    os.unlink(filepath)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    def test_format_priority(self):
        """Test that format priority is applied correctly."""
        formats_by_priority = [
            ".epub",
            ".mobi",
            ".azw",
            ".azw3",
            ".pdf",
            ".lrf",
        ]

        for i, format1 in enumerate(formats_by_priority):
            for j, format2 in enumerate(formats_by_priority):
                if i < j:  # format1 should have higher priority than format2
                    priority1 = FORMAT_PRIORITY.get(format1, 0)
                    priority2 = FORMAT_PRIORITY.get(format2, 0)
                    self.assertGreater(
                        priority1,
                        priority2,
                        f"{format1} should have higher priority than {format2}",
                    )

    def test_comic_book_format_support(self):
        """Test CBR and CBZ comic book format support."""
        # Test CBR files
        self.assertTrue(is_ebook_file("comic.cbr"))
        self.assertTrue(is_ebook_file("COMIC.CBR"))  # Case insensitive

        # Test CBZ files
        self.assertTrue(is_ebook_file("comic.cbz"))
        self.assertTrue(is_ebook_file("COMIC.CBZ"))  # Case insensitive

        # Test with allowed extensions including comics
        comic_extensions = [".epub", ".cbr", ".cbz"]
        self.assertTrue(is_ebook_file("book.epub", comic_extensions))
        self.assertTrue(is_ebook_file("comic.cbr", comic_extensions))
        self.assertTrue(is_ebook_file("comic.cbz", comic_extensions))
        self.assertFalse(is_ebook_file("book.pdf", comic_extensions))

    def test_comic_book_format_priority(self):
        """Test that comic book formats have correct priority in onefile mode."""
        from ebook_manager.core import FORMAT_PRIORITY

        # CBZ should have higher priority than CBR
        self.assertGreater(FORMAT_PRIORITY[".cbz"], FORMAT_PRIORITY[".cbr"])

        # Traditional ebook formats should have higher priority than comics
        self.assertGreater(FORMAT_PRIORITY[".epub"], FORMAT_PRIORITY[".cbz"])
        self.assertGreater(FORMAT_PRIORITY[".epub"], FORMAT_PRIORITY[".cbr"])
        self.assertGreater(FORMAT_PRIORITY[".pdf"], FORMAT_PRIORITY[".cbz"])
        self.assertGreater(FORMAT_PRIORITY[".pdf"], FORMAT_PRIORITY[".cbr"])

    def test_onefile_filtering_with_comics(self):
        """Test one-file filtering with comic book formats."""
        # Create test files with comic formats
        test_files = [
            "/path/to/Fables - Vol 1.epub",
            "/path/to/Fables - Vol 1.cbr",
            "/path/to/Fables - Vol 1.cbz",
            "/path/to/Watchmen - Chapter 1.cbr",
            "/path/to/Watchmen - Chapter 1.cbz",
        ]

        filtered = filter_onefile_per_book(test_files)

        # Should prefer EPUB over comics for Fables
        fables_result = [f for f in filtered if "Fables" in f]
        self.assertEqual(len(fables_result), 1)
        self.assertTrue(fables_result[0].endswith(".epub"))

        # Should prefer CBZ over CBR for Watchmen (no EPUB available)
        watchmen_result = [f for f in filtered if "Watchmen" in f]
        self.assertEqual(len(watchmen_result), 1)
        self.assertTrue(watchmen_result[0].endswith(".cbz"))

    # ...existing code...


class TestEbookManagerCLI(unittest.TestCase):
    """Test cases for the ebook_manager CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

        # Create a test ebook file
        self.test_file = os.path.join(self.test_dir, "test.epub")
        with open(self.test_file, "w") as f:
            f.write("Test epub content")

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        os.rmdir(self.test_dir)

    @patch("sys.argv")
    @patch("builtins.print")
    def test_main_no_arguments(self, mock_print, mock_argv):
        """Test main function with no arguments shows help."""
        mock_argv.__getitem__.side_effect = lambda x: ["ebook_manager.py"][x]
        mock_argv.__len__.return_value = 1

        ebook_manager.main()

        # Should print help information
        print_calls = [
            call_obj.args[0] for call_obj in mock_print.call_args_list
        ]
        self.assertTrue(
            any(
                "Ebook Collection Manager" in call_text
                for call_text in print_calls
            )
        )
        self.assertTrue(any("--ext" in call_text for call_text in print_calls))

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.scan_collection")
    def test_main_scan_command(self, mock_scan, mock_parse_args):
        """Test main function with scan command."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = "scan"
        mock_args.path = self.test_dir
        mock_args.ext = ".epub"
        mock_args.onefile = False
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        # Should call scan_collection with parsed extensions
        mock_scan.assert_called_once_with(self.test_dir, [".epub"], False)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.import_collection")
    def test_main_import_command_with_multiple_extensions(
        self, mock_import, mock_parse_args
    ):
        """Test main function with import command and multiple extensions."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = "import"
        mock_args.path = self.test_dir
        mock_args.ext = ".epub,.pdf,.mobi"
        mock_args.onefile = False
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        # Should call import_collection with parsed extensions
        mock_import.assert_called_once_with(
            self.test_dir, [".epub", ".pdf", ".mobi"], False
        )

    @patch("argparse.ArgumentParser.parse_args")
    @patch("builtins.print")
    def test_main_invalid_directory(self, mock_print, mock_parse_args):
        """Test main function with invalid directory path."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = "scan"
        mock_args.path = "/nonexistent/directory"
        mock_args.ext = None
        mock_parse_args.return_value = mock_args

        ebook_manager.main()

        # Should print error message
        print_calls = [
            call_obj.args[0] for call_obj in mock_print.call_args_list
        ]
        self.assertTrue(
            any(
                "Directory not found" in call_text for call_text in print_calls
            )
        )

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.scan_collection")
    def test_main_scan_command_with_onefile(self, mock_scan, mock_parse_args):
        """Test main function with scan command and --onefile option."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = "scan"
        mock_args.path = self.test_dir
        mock_args.ext = ".epub,.pdf"
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        # Should call scan_collection with extensions and onefile=True
        mock_scan.assert_called_once_with(
            self.test_dir, [".epub", ".pdf"], True
        )

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.import_collection")
    def test_main_import_command_with_onefile(
        self, mock_import, mock_parse_args
    ):
        """Test main function with import command and --onefile option."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = "import"
        mock_args.path = self.test_dir
        mock_args.ext = None
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        # Should call import_collection with onefile=True
        mock_import.assert_called_once_with(self.test_dir, None, True)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.batch_import_ebooks")
    def test_main_batch_import_with_onefile_and_ext(
        self, mock_batch_import, mock_parse_args
    ):
        """Test main function with batch-import command using --onefile and --ext."""
        # Mock command line arguments
        mock_args = MagicMock()
        mock_args.command = "batch-import"
        mock_args.path = self.test_dir
        mock_args.ext = ".epub"
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        # Should call batch_import_ebooks with both extensions and onefile=True
        mock_batch_import.assert_called_once_with(
            self.test_dir, [".epub"], True
        )


class TestCalibreIntegration(unittest.TestCase):
    """Test cases for Calibre integration functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

        # Create test ebook files
        test_books = [
            "Test Book.epub",
            "Another Book.pdf",
            "Third Book.mobi",
        ]

        for book in test_books:
            file_path = os.path.join(self.test_dir, book)
            with open(file_path, "w") as f:
                f.write("dummy content")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    @patch("ebook_manager.core.shutil.which")
    @patch("ebook_manager.core.os.path.isfile")
    def test_find_calibredb_in_path(self, mock_isfile, mock_which):
        """Test find_calibredb when calibredb is in PATH."""
        mock_which.return_value = "/usr/bin/calibredb"

        result = find_calibredb()

        mock_which.assert_called_with("calibredb")
        self.assertEqual(result, "/usr/bin/calibredb")

    @patch("ebook_manager.core.shutil.which")
    @patch("ebook_manager.core.os.path.isfile")
    def test_find_calibredb_windows_exe_in_path(self, mock_isfile, mock_which):
        """Test find_calibredb when calibredb.exe is in PATH on Windows."""

        def mock_which_side_effect(name):
            if name == "calibredb":
                return None
            elif name == "calibredb.exe":
                return "C:\\Program Files\\Calibre2\\calibredb.exe"
            return None

        mock_which.side_effect = mock_which_side_effect

        result = find_calibredb()

        self.assertEqual(result, "C:\\Program Files\\Calibre2\\calibredb.exe")

    @patch("ebook_manager.core.shutil.which")
    @patch("ebook_manager.core.os.path.isfile")
    def test_find_calibredb_fallback_paths(self, mock_isfile, mock_which):
        """Test find_calibredb when using fallback installation paths."""
        mock_which.return_value = None  # Not in PATH

        def mock_isfile_side_effect(path):
            return path == r"C:\Program Files\Calibre2\calibredb.exe"

        mock_isfile.side_effect = mock_isfile_side_effect

        result = find_calibredb()

        self.assertEqual(result, r"C:\Program Files\Calibre2\calibredb.exe")

    @patch("ebook_manager.core.shutil.which")
    @patch("ebook_manager.core.os.path.isfile")
    def test_find_calibredb_not_found(self, mock_isfile, mock_which):
        """Test find_calibredb when Calibre is not installed."""
        mock_which.return_value = None
        mock_isfile.return_value = False

        result = find_calibredb()

        self.assertIsNone(result)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.subprocess.run")
    @patch("ebook_manager.core.os.path.exists")
    def test_import_to_calibre_success(self, mock_exists, mock_run, mock_find):
        """Test successful import to Calibre."""
        mock_find.return_value = "/usr/bin/calibredb"
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "Added book ids: 123"
        mock_run.return_value = mock_result

        success, message = import_to_calibre("/path/to/book.epub")

        self.assertTrue(success)
        self.assertIn("Added book ids", message)
        mock_run.assert_called_once()

    @patch("ebook_manager.core.find_calibredb")
    def test_import_to_calibre_no_calibre(self, mock_find):
        """Test import to Calibre when Calibre is not found."""
        mock_find.return_value = None

        success, message = import_to_calibre("/path/to/book.epub")

        self.assertFalse(success)
        self.assertIn("executable not found", message)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.subprocess.run")
    @patch("ebook_manager.core.os.path.exists")
    def test_import_to_calibre_failure(self, mock_exists, mock_run, mock_find):
        """Test failed import to Calibre."""
        mock_find.return_value = "/usr/bin/calibredb"
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "calibredb")

        success, message = import_to_calibre("/path/to/book.epub")

        self.assertFalse(success)
        self.assertIn("failed", message)

    @patch("ebook_manager.__main__.find_calibredb")
    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_scan_collection_calibre_no_calibre(
        self, mock_print, mock_input, mock_find_ebooks, mock_find_calibre
    ):
        """Test scan_collection_calibre when Calibre is not found."""
        mock_find_calibre.return_value = None

        scan_collection_calibre(self.test_dir)

        # Should print error message and return early
        mock_print.assert_any_call(
            "❌ Calibre not found! Please install Calibre to use this feature."
        )
        mock_find_ebooks.assert_not_called()

    @patch("ebook_manager.__main__.find_calibredb")
    @patch("ebook_manager.__main__.find_ebooks")
    @patch("ebook_manager.__main__.import_ebook_to_calibre")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_scan_collection_calibre_success(
        self,
        mock_print,
        mock_input,
        mock_import,
        mock_find_ebooks,
        mock_find_calibre,
    ):
        """Test successful scan_collection_calibre."""
        mock_find_calibre.return_value = "/usr/bin/calibredb"
        mock_find_ebooks.return_value = [
            "/path/to/book1.epub",
            "/path/to/book2.pdf",
        ]
        mock_input.return_value = "y"
        mock_import.return_value = True

        scan_collection_calibre(self.test_dir)

        # Should find Calibre and process ebooks
        mock_print.assert_any_call("✓ Found Calibre at: /usr/bin/calibredb")
        self.assertEqual(mock_import.call_count, 2)

    @patch("ebook_manager.__main__.find_calibredb")
    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_scan_collection_calibre_cancelled(
        self, mock_print, mock_input, mock_find_ebooks, mock_find_calibre
    ):
        """Test scan_collection_calibre when user cancels."""
        mock_find_calibre.return_value = "/usr/bin/calibredb"
        mock_find_ebooks.return_value = ["/path/to/book.epub"]
        mock_input.return_value = "n"

        scan_collection_calibre(self.test_dir)

        mock_print.assert_any_call("Import cancelled.")

    @patch("ebook_manager.__main__.find_calibredb")
    @patch("ebook_manager.__main__.import_ebook_to_beets")
    @patch("ebook_manager.__main__.import_ebook_to_calibre")
    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.input")
    @patch("builtins.print")
    @patch("os.path.exists")
    def test_import_collection_dual_both_available(
        self,
        mock_exists,
        mock_print,
        mock_input,
        mock_find_ebooks,
        mock_calibre_import,
        mock_beets_import,
        mock_find_calibre,
    ):
        """Test dual import when both beets and Calibre are available."""
        mock_find_calibre.return_value = "/usr/bin/calibredb"
        mock_exists.return_value = True  # BEETS_EXE exists
        mock_find_ebooks.return_value = ["/path/to/book.epub"]
        mock_input.return_value = "y"
        mock_beets_import.return_value = "Successfully imported"
        mock_calibre_import.return_value = True

        import_collection_dual(self.test_dir)

        mock_print.assert_any_call("✓ Using: beets + Calibre")
        mock_beets_import.assert_called_once()
        mock_calibre_import.assert_called_once()

    @patch("ebook_manager.__main__.find_calibredb")
    @patch("ebook_manager.__main__.find_ebooks")
    @patch("builtins.print")
    @patch("os.path.exists")
    def test_import_collection_dual_neither_available(
        self, mock_exists, mock_print, mock_find_ebooks, mock_find_calibre
    ):
        """Test dual import when neither beets nor Calibre are available."""
        mock_find_calibre.return_value = None
        mock_exists.return_value = False

        import_collection_dual(self.test_dir)

        mock_print.assert_any_call("❌ Neither beets nor Calibre found!")
        mock_find_ebooks.assert_not_called()

    def test_import_ebook_to_calibre_success(self):
        """Test successful import_ebook_to_calibre wrapper function."""
        with patch("ebook_manager.__main__.import_to_calibre") as mock_import:
            mock_import.return_value = (True, "Import successful")

            result = import_ebook_to_calibre("/path/to/book.epub")

            self.assertTrue(result)
            mock_import.assert_called_once_with(
                "/path/to/book.epub", verbose=True
            )

    def test_import_ebook_to_calibre_failure(self):
        """Test failed import_ebook_to_calibre wrapper function."""
        with patch("ebook_manager.__main__.import_to_calibre") as mock_import:
            mock_import.return_value = (False, "Import failed")

            result = import_ebook_to_calibre("/path/to/book.epub")

            self.assertFalse(result)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.subprocess.run")
    def test_find_books_in_calibre_success(self, mock_run, mock_find):
        """Test successful search for books in Calibre by path."""
        mock_find.return_value = "/usr/bin/calibredb"
        mock_result = MagicMock()
        # New format: id,title,formats where formats contain file paths
        mock_result.stdout = (
            "id\ttitle\tformats\n"
            "123\tTest Book\t/old/path/book.epub\n"
            "456\tAnother Book\t/old/path/another.pdf,/old/path/another.epub"
        )
        mock_run.return_value = mock_result

        result = find_books_in_calibre("/old/path/book.epub")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "123")
        self.assertEqual(result[0]["path"], "/old/path/book.epub")
        self.assertEqual(result[0]["title"], "Test Book")

    @patch("ebook_manager.core.find_calibredb")
    def test_find_books_in_calibre_no_calibre(self, mock_find):
        """Test find_books_in_calibre when Calibre is not found."""
        mock_find.return_value = None

        result = find_books_in_calibre("/old/path/book.epub")

        self.assertEqual(result, [])

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.subprocess.run")
    @patch("os.path.exists")
    def test_update_calibre_book_path_success(
        self, mock_exists, mock_run, mock_find
    ):
        """Test successful update of Calibre book path."""
        mock_find.return_value = "/usr/bin/calibredb"
        mock_exists.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "Added book ids: 789"
        mock_run.return_value = mock_result

        result = update_calibre_book_path(
            "123", "/old/path/book.epub", "/new/path/book.epub"
        )

        self.assertTrue(result)
        # Verify two calls: add and remove
        self.assertEqual(mock_run.call_count, 2)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.find_books_in_calibre")
    @patch("ebook_manager.core.update_calibre_book_path")
    @patch("builtins.print")
    def test_sync_calibre_after_move_success(
        self, mock_print, mock_update, mock_find_books, mock_find
    ):
        """Test successful sync of Calibre database after file moves."""
        mock_find.return_value = "/usr/bin/calibredb"
        mock_find_books.return_value = [
            {"id": "123", "path": "/old/path/book.epub"}
        ]
        mock_update.return_value = True

        old_paths = ["/old/path/book.epub"]
        new_paths = ["/new/path/book.epub"]

        result = sync_calibre_after_move(old_paths, new_paths)

        self.assertEqual(result["updated"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["not_in_calibre"], 0)

    @patch("ebook_manager.core.find_calibredb")
    def test_sync_calibre_after_move_no_calibre(self, mock_find):
        """Test sync when Calibre is not found."""
        mock_find.return_value = None

        old_paths = ["/old/path/book.epub"]
        new_paths = ["/new/path/book.epub"]

        result = sync_calibre_after_move(old_paths, new_paths)

        self.assertEqual(result["updated"], 0)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["not_in_calibre"], 0)

    def test_sync_calibre_after_move_mismatched_paths(self):
        """Test sync with mismatched path counts."""
        old_paths = ["/old/path/book1.epub", "/old/path/book2.epub"]
        new_paths = ["/new/path/book1.epub"]

        with self.assertRaises(ValueError):
            sync_calibre_after_move(old_paths, new_paths)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.subprocess.run")
    def test_sync_calibre_with_beets_library_success(
        self, mock_run, mock_find
    ):
        """Test successful sync of Calibre with beets library using metadata."""
        mock_find.return_value = "/usr/bin/calibredb"

        # Mock beets library query with metadata format: path|artist|album|title
        beets_result = MagicMock()
        beets_result.returncode = 0
        beets_result.stdout = (
            "/path/to/book1.epub|Isaac Asimov|Foundation|Foundation\n"
            "/path/to/book2.pdf|Douglas Adams|Hitchhiker's Guide|"
            "The Hitchhiker's Guide to the Galaxy"
        )

        # Mock Calibre library query with JSON format
        calibre_result = MagicMock()
        calibre_result.returncode = 0
        calibre_result.stdout = """[
            {"id": "1", "title": "Foundation", "authors": "Isaac Asimov"},
            {"id": "2", "title": "The Hitchhiker's Guide to the Galaxy",
             "authors": "Douglas Adams"}
        ]"""

        mock_run.side_effect = [beets_result, calibre_result]

        stats = sync_calibre_with_beets_library()

        # Check the results for metadata-based matching
        self.assertEqual(stats["scanned"], 2)
        self.assertEqual(stats["updated"], 2)  # Both books found in Calibre
        self.assertEqual(stats["not_in_calibre"], 0)
        self.assertEqual(len(stats["missing_paths"]), 0)
        self.assertFalse("error" in stats)

    @patch("ebook_manager.core.find_calibredb")
    def test_sync_calibre_with_beets_library_no_calibre(self, mock_find):
        """Test sync when Calibre is not found."""
        mock_find.return_value = None

        stats = sync_calibre_with_beets_library()

        self.assertIn("error", stats)
        self.assertEqual(stats["updated"], 0)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.subprocess.run")
    def test_sync_calibre_with_beets_library_missing_books(
        self, mock_run, mock_find
    ):
        """Test sync when some books are missing from Calibre."""
        mock_find.return_value = "/usr/bin/calibredb"

        # Mock beets library query - 3 books
        beets_result = MagicMock()
        beets_result.returncode = 0
        beets_result.stdout = (
            "/path/to/book1.epub|Isaac Asimov|Foundation|Foundation\n"
            "/path/to/book2.pdf|Douglas Adams|Hitchhiker's Guide|"
            "The Hitchhiker's Guide to the Galaxy\n"
            "/path/to/book3.mobi|Philip K. Dick|Do Androids Dream|"
            "Do Androids Dream of Electric Sheep?"
        )

        # Mock Calibre library query - only 1 book (Foundation)
        calibre_result = MagicMock()
        calibre_result.returncode = 0
        calibre_result.stdout = """[
            {"id": "1", "title": "Foundation", "authors": "Isaac Asimov"}
        ]"""

        mock_run.side_effect = [beets_result, calibre_result]

        stats = sync_calibre_with_beets_library()

        # Check that missing books are correctly identified
        self.assertEqual(stats["scanned"], 3)
        self.assertEqual(
            stats["updated"], 1
        )  # Only Foundation found in Calibre
        self.assertEqual(stats["not_in_calibre"], 2)  # 2 books missing
        self.assertEqual(len(stats["missing_paths"]), 2)  # 2 missing paths

        # Check the specific missing paths
        expected_missing = ["/path/to/book2.pdf", "/path/to/book3.mobi"]
        self.assertEqual(
            sorted(stats["missing_paths"]), sorted(expected_missing)
        )

        self.assertFalse("error" in stats)


class TestCalibreCommands(unittest.TestCase):
    """Test cases for Calibre CLI commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.test_dir)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.scan_collection_calibre")
    def test_main_calibre_scan_command(self, mock_scan, mock_parse_args):
        """Test main function with calibre-scan command."""
        mock_args = MagicMock()
        mock_args.command = "calibre-scan"
        mock_args.path = self.test_dir
        mock_args.ext = None
        mock_args.onefile = False
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        mock_scan.assert_called_once_with(self.test_dir, None, False)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.scan_collection_calibre")
    def test_main_calibre_import_command(self, mock_scan, mock_parse_args):
        """Test main function with calibre-import command."""
        mock_args = MagicMock()
        mock_args.command = "calibre-import"
        mock_args.path = self.test_dir
        mock_args.ext = ".epub"
        mock_args.onefile = True
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        mock_scan.assert_called_once_with(self.test_dir, [".epub"], True)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.import_collection_dual")
    def test_main_dual_import_command(self, mock_dual, mock_parse_args):
        """Test main function with dual-import command."""
        mock_args = MagicMock()
        mock_args.command = "dual-import"
        mock_args.path = self.test_dir
        mock_args.ext = ".epub,.pdf"
        mock_args.onefile = False
        mock_parse_args.return_value = mock_args

        with patch("os.path.isdir", return_value=True):
            ebook_manager.main()

        mock_dual.assert_called_once_with(
            self.test_dir, [".epub", ".pdf"], False
        )

    # Tests for new Calibre database import and synchronization features

    @patch("ebook_manager.core.find_calibredb")
    def test_get_all_calibre_books_no_calibre(
        self, mock_find_calibredb: MagicMock
    ) -> None:
        """Test get_all_calibre_books when Calibre is not found."""
        mock_find_calibredb.return_value = None

        result = get_all_calibre_books()

        self.assertEqual(result, [])

    @patch("ebook_manager.core.find_calibredb")
    @patch("subprocess.run")
    def test_get_all_calibre_books_success(
        self, mock_subprocess, mock_find_calibredb
    ):
        """Test successful retrieval of Calibre books."""
        mock_find_calibredb.return_value = "calibredb"

        # Mock the initial list command
        mock_list_result = MagicMock()
        mock_list_result.stdout = """[
            {
                "id": 1,
                "title": "Test Book",
                "authors": "Test Author",
                "path": "Test Author/Test Book (1)",
                "formats": ["EPUB", "PDF"],
                "uuid": "test-uuid-123"
            }
        ]"""
        mock_list_result.returncode = 0

        # Mock the path lookup command
        mock_path_result = MagicMock()
        mock_path_result.stdout = (
            "/path/to/library/Test Author/Test Book (1)/Test Book.epub\n"
        )
        mock_path_result.returncode = 0

        mock_subprocess.side_effect = [mock_list_result, mock_path_result]

        with patch("os.path.exists", return_value=True):
            result = get_all_calibre_books()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Book")
        self.assertEqual(result[0]["authors"], "Test Author")
        self.assertIn("file_paths", result[0])

    @patch("ebook_manager.core.find_calibredb")
    @patch("os.path.exists")
    def test_import_calibre_database_to_beets_no_calibre(
        self, mock_exists, mock_find_calibredb
    ):
        """Test import function when Calibre is not found."""
        mock_find_calibredb.return_value = None
        mock_exists.return_value = True  # beets exists

        result = import_calibre_database_to_beets("fake_beets_exe")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Calibre not found")
        self.assertEqual(result["imported"], 0)

    @patch("ebook_manager.core.find_calibredb")
    @patch("os.path.exists")
    def test_import_calibre_database_to_beets_no_beets(
        self, mock_exists, mock_find_calibredb
    ):
        """Test import function when beets is not found."""
        mock_find_calibredb.return_value = "calibredb"
        mock_exists.return_value = False  # beets doesn't exist

        result = import_calibre_database_to_beets("fake_beets_exe")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Beets not found")
        self.assertEqual(result["imported"], 0)

    @patch("ebook_manager.core.find_calibredb")
    @patch("os.path.exists")
    @patch("ebook_manager.core.get_all_calibre_books")
    def test_import_calibre_database_to_beets_no_books(
        self, mock_get_books, mock_exists, mock_find_calibredb
    ):
        """Test import function when no Calibre books are found."""
        mock_find_calibredb.return_value = "calibredb"
        mock_exists.return_value = True
        mock_get_books.return_value = []

        result = import_calibre_database_to_beets("beets_exe")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "No books found in Calibre database")
        self.assertEqual(result["imported"], 0)

    @patch("ebook_manager.core.find_calibredb")
    @patch("os.path.exists")
    @patch("ebook_manager.core.get_all_calibre_books")
    @patch("subprocess.run")
    def test_import_calibre_database_to_beets_dry_run(
        self, mock_subprocess, mock_get_books, mock_exists, mock_find_calibredb
    ):
        """Test import function in dry run mode."""
        mock_find_calibredb.return_value = "calibredb"
        mock_exists.return_value = True

        # Mock Calibre books
        mock_books = [
            {
                "id": 1,
                "title": "Test Book",
                "authors": "Test Author",
                "file_paths": ["/path/to/test/book.epub"],
            }
        ]
        mock_get_books.return_value = mock_books

        # Mock beets query for existing books
        mock_beets_result = MagicMock()
        mock_beets_result.stdout = ""  # No existing books
        mock_beets_result.returncode = 0
        mock_subprocess.return_value = mock_beets_result

        result = import_calibre_database_to_beets("beets_exe", dry_run=True)

        self.assertEqual(result["total_books"], 1)
        self.assertEqual(result["imported"], 1)  # Would import in dry run
        self.assertEqual(result["failed"], 0)

    @patch("ebook_manager.core.find_calibredb")
    @patch("ebook_manager.core.import_calibre_database_to_beets")
    def test_reverse_calibre_sync_success(
        self, mock_import, mock_find_calibredb
    ):
        """Test reverse sync function."""
        mock_find_calibredb.return_value = "calibredb"
        mock_import.return_value = {
            "total_books": 5,
            "imported": 3,
            "skipped": 2,
            "failed": 0,
            "errors": [],
        }

        result = reverse_calibre_sync("beets_exe")

        self.assertEqual(result["total_books"], 5)
        self.assertEqual(result["imported"], 3)
        self.assertEqual(result["skipped"], 2)
        mock_import.assert_called_once()

    @patch("ebook_manager.core.sync_calibre_with_beets_library")
    @patch("ebook_manager.core.import_calibre_database_to_beets")
    def test_bidirectional_calibre_sync(self, mock_import, mock_sync):
        """Test bidirectional sync function."""
        # Mock Calibre -> beets import
        mock_import.return_value = {
            "total_books": 5,
            "imported": 2,
            "skipped": 3,
            "failed": 0,
            "errors": [],
        }

        # Mock beets -> Calibre sync
        mock_sync.return_value = {
            "scanned": 10,
            "updated": 3,
            "failed": 0,
            "not_in_calibre": 2,
        }

        result = bidirectional_calibre_sync("beets_exe", dry_run=False)

        # Test that it returns a proper structure
        self.assertIsInstance(result, dict)
        mock_import.assert_called_once()
        mock_sync.assert_called_once()

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("ebook_manager.core.import_calibre_database_to_beets")
    def test_import_from_calibre_database_cli_success(
        self, mock_import, mock_print, mock_input
    ):
        """Test CLI wrapper for Calibre database import."""
        mock_input.return_value = "y"  # User says yes
        mock_import.return_value = {
            "total_books": 3,
            "imported": 3,
            "skipped": 0,
            "failed": 0,
            "errors": [],
        }

        import_from_calibre_database(dry_run=False)

        mock_import.assert_called_once()
        # Check that success message was printed
        success_calls = [
            call
            for call in mock_print.call_args_list
            if "SUCCESS!" in str(call)
        ]
        self.assertTrue(len(success_calls) > 0)

    @patch("builtins.input")
    @patch("builtins.print")
    def test_import_from_calibre_database_cli_cancelled(
        self, mock_print, mock_input
    ):
        """Test CLI wrapper when user cancels."""
        mock_input.return_value = "n"  # User says no

        import_from_calibre_database(dry_run=False)

        # Check that cancelled message was printed
        cancel_calls = [
            call
            for call in mock_print.call_args_list
            if "cancelled" in str(call).lower()
        ]
        self.assertTrue(len(cancel_calls) > 0)

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("ebook_manager.core.bidirectional_calibre_sync")
    def test_bidirectional_sync_workflow_cli(
        self, mock_sync, mock_print, mock_input
    ):
        """Test CLI wrapper for bidirectional sync."""
        mock_input.return_value = "y"  # User says yes
        mock_sync.return_value = {
            "total_calibre_books": 5,
            "calibre_to_beets_imported": 2,
            "beets_to_calibre_imported": 1,
            "calibre_to_beets_skipped": 3,
            "calibre_to_beets_failed": 0,
            "beets_to_calibre_failed": 0,
            "sync_successful": True,
        }

        bidirectional_sync_workflow(dry_run=False)

        mock_sync.assert_called_once()
        # Check that success message was printed
        success_calls = [
            call
            for call in mock_print.call_args_list
            if "COMPLETE!" in str(call)
        ]
        self.assertTrue(len(success_calls) > 0)

    @patch("builtins.input")
    @patch("builtins.print")
    @patch("ebook_manager.core.reverse_calibre_sync")
    def test_reverse_sync_workflow_cli(
        self, mock_sync, mock_print, mock_input
    ):
        """Test CLI wrapper for reverse sync."""
        mock_input.return_value = "y"  # User says yes
        mock_sync.return_value = {
            "total_books": 5,
            "imported": 2,
            "skipped": 3,
            "failed": 0,
            "errors": [],
        }

        reverse_sync_workflow()

        mock_sync.assert_called_once()
        # Check that success message was printed
        success_calls = [
            call
            for call in mock_print.call_args_list
            if "COMPLETE!" in str(call)
        ]
        self.assertTrue(len(success_calls) > 0)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.import_from_calibre_database")
    def test_main_import_from_calibre_command(
        self, mock_import, mock_parse_args
    ):
        """Test main function with import-from-calibre command."""
        mock_args = MagicMock()
        mock_args.command = "import-from-calibre"
        mock_args.dry_run = True
        mock_parse_args.return_value = mock_args

        import ebook_manager

        ebook_manager.main()

        mock_import.assert_called_once_with(dry_run=True)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.bidirectional_sync_workflow")
    def test_main_bidirectional_sync_command(self, mock_sync, mock_parse_args):
        """Test main function with bidirectional-sync command."""
        mock_args = MagicMock()
        mock_args.command = "bidirectional-sync"
        mock_args.dry_run = False
        mock_parse_args.return_value = mock_args

        import ebook_manager

        ebook_manager.main()

        mock_sync.assert_called_once_with(dry_run=False)

    @patch("argparse.ArgumentParser.parse_args")
    @patch("ebook_manager.__main__.reverse_sync_workflow")
    def test_main_reverse_sync_command(self, mock_sync, mock_parse_args):
        """Test main function with reverse-sync command."""
        mock_args = MagicMock()
        mock_args.command = "reverse-sync"
        mock_parse_args.return_value = mock_args

        import ebook_manager

        ebook_manager.main()

        mock_sync.assert_called_once()
