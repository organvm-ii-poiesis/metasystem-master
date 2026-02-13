#!/usr/bin/env python3
"""
iTerm2 Content Extractor

Extracts content from iTerm2 windows using Python API.
"""

import subprocess
from datetime import datetime
import sys


class ITerm2Extractor:
    """Extract content from iTerm2 windows."""

    def __init__(self):
        """Initialize iTerm2 extractor."""
        self.terminal_type = 'iterm2'
        self._check_iterm2_api()

    def _check_iterm2_api(self):
        """Check if iTerm2 Python API is available."""
        try:
            import iterm2
            self.iterm2 = iterm2
            self.api_available = True
        except ImportError:
            print("⚠️  iTerm2 Python API not installed")
            print("   Install with: pip install iterm2")
            self.api_available = False
            self.iterm2 = None

    def is_available(self):
        """Check if iTerm2 is running."""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to (name of processes) contains "iTerm"'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() == 'true'
        except:
            return False

    def get_window_count(self):
        """Get number of iTerm2 windows."""
        script = '''
        tell application "iTerm"
            return count of windows
        end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            return int(result.stdout.strip())
        except:
            return 0

    def get_window_content_via_applescript(self, window_index=1):
        """
        Get content from iTerm2 window using AppleScript.

        Falls back to AppleScript if Python API is unavailable.

        Args:
            window_index (int): Window index (1-based)

        Returns:
            tuple: (content, metadata) or (None, None)
        """
        script = f'''
        tell application "iTerm"
            if (count of windows) >= {window_index} then
                set windowName to name of window {window_index}
                set tabCount to count of tabs of window {window_index}

                -- Get content from first session of first tab
                set sessionContents to ""
                if tabCount > 0 then
                    set sessionContents to contents of first session of first tab of window {window_index}
                end if

                return sessionContents & "|||METADATA|||" & windowName & "|||" & tabCount
            else
                return "NO_WINDOW"
            end if
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"AppleScript error: {result.stderr}")
                return None, None

            output = result.stdout.strip()

            if output == "NO_WINDOW":
                return None, None

            # Parse output
            if '|||METADATA|||' in output:
                parts = output.split('|||METADATA|||')
                content = parts[0]
                meta_parts = parts[1].split('|||')
                window_name = meta_parts[0] if len(meta_parts) > 0 else "Unknown"
                tab_count = meta_parts[1] if len(meta_parts) > 1 else "1"
            else:
                content = output
                window_name = "Unknown"
                tab_count = "1"

            metadata = {
                'terminal_type': self.terminal_type,
                'window_title': window_name,
                'window_index': window_index,
                'tab_count': int(tab_count),
                'captured_at': datetime.now().isoformat()
            }

            return content, metadata

        except subprocess.TimeoutExpired:
            print(f"Timeout getting window {window_index} content")
            return None, None
        except Exception as e:
            print(f"Error getting window content: {e}")
            return None, None

    def get_window_content(self, window_index=1):
        """
        Get content from iTerm2 window.

        Tries Python API first, falls back to AppleScript.

        Args:
            window_index (int): Window index (1-based)

        Returns:
            tuple: (content, metadata) or (None, None)
        """
        if self.api_available:
            # Try Python API first (not implemented yet - complex async)
            pass

        # Fall back to AppleScript
        return self.get_window_content_via_applescript(window_index)

    def get_all_windows_content(self):
        """
        Get content from all iTerm2 windows.

        Returns:
            list: List of (content, metadata) tuples
        """
        results = []
        window_count = self.get_window_count()

        for i in range(1, window_count + 1):
            content, metadata = self.get_window_content(i)
            if content is not None:
                results.append((content, metadata))

        return results

    def get_frontmost_window_content(self):
        """
        Get content from the frontmost iTerm2 window.

        Returns:
            tuple: (content, metadata) or (None, None)
        """
        script = '''
        tell application "iTerm"
            if (count of windows) > 0 then
                set frontWindow to front window
                set windowName to name of frontWindow
                set tabCount to count of tabs of frontWindow

                -- Get content from first session of first tab
                set sessionContents to ""
                if tabCount > 0 then
                    set sessionContents to contents of first session of first tab of frontWindow
                end if

                return sessionContents & "|||METADATA|||" & windowName & "|||" & tabCount
            else
                return "NO_WINDOW"
            end if
        end tell
        '''

        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None, None

            output = result.stdout.strip()

            if output == "NO_WINDOW":
                return None, None

            # Parse output
            if '|||METADATA|||' in output:
                parts = output.split('|||METADATA|||')
                content = parts[0]
                meta_parts = parts[1].split('|||')
                window_name = meta_parts[0] if len(meta_parts) > 0 else "Unknown"
                tab_count = meta_parts[1] if len(meta_parts) > 1 else "1"
            else:
                content = output
                window_name = "Unknown"
                tab_count = "1"

            metadata = {
                'terminal_type': self.terminal_type,
                'window_title': window_name,
                'tab_count': int(tab_count),
                'captured_at': datetime.now().isoformat()
            }

            return content, metadata

        except Exception as e:
            print(f"Error getting frontmost window: {e}")
            return None, None


def main():
    """CLI interface for iTerm2 extractor."""
    import argparse

    parser = argparse.ArgumentParser(description='iTerm2 Content Extractor')
    parser.add_argument('--check', action='store_true', help='Check if iTerm2 is available')
    parser.add_argument('--count', action='store_true', help='Count iTerm2 windows')
    parser.add_argument('--capture', type=int, metavar='WINDOW', help='Capture specific window')
    parser.add_argument('--capture-all', action='store_true', help='Capture all windows')
    parser.add_argument('--frontmost', action='store_true', help='Capture frontmost window')
    parser.add_argument('--export', action='store_true', help='Export captured content to file')

    args = parser.parse_args()

    extractor = ITerm2Extractor()

    if args.check:
        available = extractor.is_available()
        print(f"iTerm2 available: {available}")

    elif args.count:
        count = extractor.get_window_count()
        print(f"iTerm2 windows: {count}")

    elif args.capture is not None:
        content, metadata = extractor.get_window_content(args.capture)
        if content:
            print(f"\n📋 Window {args.capture} Content:")
            print(f"Title: {metadata['window_title']}")
            print(f"Tabs: {metadata['tab_count']}")
            print(f"\n{'=' * 80}")
            print(content[:1000])  # Show first 1000 chars
            if len(content) > 1000:
                print(f"\n... ({len(content) - 1000} more characters)")

            if args.export:
                from terminal_export_manager import TerminalExportManager
                manager = TerminalExportManager()
                filepath = manager.export_session(content, metadata)
                print(f"\n✅ Exported to: {filepath}")
        else:
            print(f"❌ Could not capture window {args.capture}")

    elif args.capture_all:
        results = extractor.get_all_windows_content()
        print(f"\n📋 Captured {len(results)} windows")

        if args.export:
            from terminal_export_manager import TerminalExportManager
            manager = TerminalExportManager()

            for i, (content, metadata) in enumerate(results, 1):
                filepath = manager.export_session(content, metadata)
                print(f"✅ Window {i} exported to: {filepath}")

    elif args.frontmost:
        content, metadata = extractor.get_frontmost_window_content()
        if content:
            print(f"\n📋 Frontmost Window Content:")
            print(f"Title: {metadata['window_title']}")
            print(f"Tabs: {metadata['tab_count']}")
            print(f"\n{'=' * 80}")
            print(content[:1000])  # Show first 1000 chars
            if len(content) > 1000:
                print(f"\n... ({len(content) - 1000} more characters)")

            if args.export:
                from terminal_export_manager import TerminalExportManager
                manager = TerminalExportManager()
                filepath = manager.export_session(content, metadata)
                print(f"\n✅ Exported to: {filepath}")
        else:
            print("❌ Could not capture frontmost window")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
