#!/usr/bin/env python3
"""
Terminal.app Content Extractor

Extracts content from Terminal.app windows using AppleScript.
"""

import subprocess
import re
from datetime import datetime


class TerminalAppExtractor:
    """Extract content from Terminal.app windows."""

    def __init__(self):
        """Initialize Terminal.app extractor."""
        self.terminal_type = 'terminal_app'

    def is_available(self):
        """Check if Terminal.app is available."""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to (name of processes) contains "Terminal"'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() == 'true'
        except:
            return False

    def get_window_count(self):
        """Get number of Terminal windows."""
        script = '''
        tell application "Terminal"
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

    def get_window_content(self, window_index=1):
        """
        Get content from a Terminal window.

        Args:
            window_index (int): Window index (1-based)

        Returns:
            tuple: (content, metadata) or (None, None) if failed
        """
        # AppleScript to get window content
        script = f'''
        tell application "Terminal"
            if (count of windows) >= {window_index} then
                set windowName to name of window {window_index}
                set windowContents to contents of window {window_index}
                set tabCount to count of tabs of window {window_index}

                return windowContents & "|||METADATA|||" & windowName & "|||" & tabCount
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

    def get_all_windows_content(self):
        """
        Get content from all Terminal windows.

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
        Get content from the frontmost Terminal window.

        Returns:
            tuple: (content, metadata) or (None, None)
        """
        script = '''
        tell application "Terminal"
            if (count of windows) > 0 then
                set frontWindow to front window
                set windowName to name of frontWindow
                set windowContents to contents of frontWindow
                set tabCount to count of tabs of frontWindow

                return windowContents & "|||METADATA|||" & windowName & "|||" & tabCount
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

    def watch_for_window_close(self, callback):
        """
        Watch for window close events (polling-based).

        Args:
            callback: Function to call when window closes, receives (content, metadata)

        Note: This is a simple polling implementation. For production,
        consider using more sophisticated event monitoring.
        """
        import time

        previous_count = self.get_window_count()
        print(f"Monitoring Terminal.app windows (current count: {previous_count})")

        try:
            while True:
                time.sleep(1)  # Poll every second
                current_count = self.get_window_count()

                if current_count < previous_count:
                    print(f"⚠️  Window closed! (was {previous_count}, now {current_count})")
                    # Window was closed - try to capture remaining windows
                    # (We can't get the closed window's content, only remaining ones)
                    # For now, just notify
                    callback(None, {'event': 'window_closed', 'timestamp': datetime.now().isoformat()})

                previous_count = current_count

        except KeyboardInterrupt:
            print("\n⏹  Stopped monitoring")


def main():
    """CLI interface for Terminal.app extractor."""
    import argparse

    parser = argparse.ArgumentParser(description='Terminal.app Content Extractor')
    parser.add_argument('--check', action='store_true', help='Check if Terminal.app is available')
    parser.add_argument('--count', action='store_true', help='Count Terminal windows')
    parser.add_argument('--capture', type=int, metavar='WINDOW', help='Capture specific window')
    parser.add_argument('--capture-all', action='store_true', help='Capture all windows')
    parser.add_argument('--frontmost', action='store_true', help='Capture frontmost window')
    parser.add_argument('--export', action='store_true', help='Export captured content to file')

    args = parser.parse_args()

    extractor = TerminalAppExtractor()

    if args.check:
        available = extractor.is_available()
        print(f"Terminal.app available: {available}")

    elif args.count:
        count = extractor.get_window_count()
        print(f"Terminal windows: {count}")

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
