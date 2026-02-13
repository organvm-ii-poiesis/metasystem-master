#!/usr/bin/env python3
"""
Terminal Monitor Daemon

Background daemon that monitors terminal windows and auto-exports on close.
Supports Terminal.app and iTerm2.
"""

import time
import logging
import sys
from pathlib import Path
from datetime import datetime
from terminal_export_manager import TerminalExportManager
from terminal_app_extractor import TerminalAppExtractor
from iterm2_extractor import ITerm2Extractor


# Setup logging
log_dir = Path.home() / '.metasystem' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'terminal_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('TerminalMonitor')


class TerminalMonitor:
    """Monitor terminal windows and auto-export on close."""

    def __init__(self):
        """Initialize terminal monitor."""
        self.export_manager = TerminalExportManager()
        self.terminal_app = TerminalAppExtractor()
        self.iterm2 = ITerm2Extractor()

        self.previous_state = {
            'terminal_app': self.get_terminal_app_state(),
            'iterm2': self.get_iterm2_state()
        }

        logger.info("Terminal Monitor initialized")
        logger.info(f"Terminal.app available: {self.terminal_app.is_available()}")
        logger.info(f"iTerm2 available: {self.iterm2.is_available()}")

    def get_terminal_app_state(self):
        """Get current state of Terminal.app windows."""
        if not self.terminal_app.is_available():
            return {'count': 0, 'windows': {}}

        count = self.terminal_app.get_window_count()
        windows = {}

        for i in range(1, count + 1):
            content, metadata = self.terminal_app.get_window_content(i)
            if content:
                # Use window title as key
                key = f"terminal_app_{i}_{metadata.get('window_title', 'unknown')}"
                windows[key] = {
                    'index': i,
                    'title': metadata.get('window_title'),
                    'content_hash': hash(content[:1000])  # Hash first 1000 chars
                }

        return {'count': count, 'windows': windows}

    def get_iterm2_state(self):
        """Get current state of iTerm2 windows."""
        if not self.iterm2.is_available():
            return {'count': 0, 'windows': {}}

        count = self.iterm2.get_window_count()
        windows = {}

        for i in range(1, count + 1):
            content, metadata = self.iterm2.get_window_content(i)
            if content:
                # Use window title as key
                key = f"iterm2_{i}_{metadata.get('window_title', 'unknown')}"
                windows[key] = {
                    'index': i,
                    'title': metadata.get('window_title'),
                    'content_hash': hash(content[:1000])
                }

        return {'count': count, 'windows': windows}

    def check_for_closed_windows(self):
        """Check if any windows have closed."""
        current_state = {
            'terminal_app': self.get_terminal_app_state(),
            'iterm2': self.get_iterm2_state()
        }

        closed_windows = []

        # Check Terminal.app
        if self.terminal_app.is_available():
            prev_windows = self.previous_state['terminal_app']['windows']
            curr_windows = current_state['terminal_app']['windows']

            for window_key in prev_windows.keys():
                if window_key not in curr_windows:
                    closed_windows.append({
                        'terminal': 'terminal_app',
                        'title': prev_windows[window_key]['title'],
                        'index': prev_windows[window_key]['index']
                    })

        # Check iTerm2
        if self.iterm2.is_available():
            prev_windows = self.previous_state['iterm2']['windows']
            curr_windows = current_state['iterm2']['windows']

            for window_key in prev_windows.keys():
                if window_key not in curr_windows:
                    closed_windows.append({
                        'terminal': 'iterm2',
                        'title': prev_windows[window_key]['title'],
                        'index': prev_windows[window_key]['index']
                    })

        # Update state
        self.previous_state = current_state

        return closed_windows

    def export_closed_window(self, window_info):
        """
        Export a closed window if we can.

        Note: We can't get the content of a closed window,
        so we log the event and metadata instead.
        """
        logger.info(f"Window closed: {window_info['terminal']} - {window_info['title']}")

        # Create a metadata-only export
        content = f"""# Terminal Window Close Event

Window: {window_info['title']}
Terminal: {window_info['terminal']}
Closed at: {datetime.now().isoformat()}

(Note: Content could not be captured as window was already closed)
(Recommendation: Use export_terminal.sh before closing windows to capture content)
"""

        metadata = {
            'terminal_type': window_info['terminal'],
            'window_title': window_info['title'],
            'event': 'window_closed',
            'captured_at': datetime.now().isoformat()
        }

        try:
            filepath = self.export_manager.export_session(content, metadata)
            if filepath:
                logger.info(f"Event exported: {filepath}")
        except Exception as e:
            logger.error(f"Failed to export window close event: {e}")

    def run(self, check_interval=1):
        """
        Run the terminal monitor daemon.

        Args:
            check_interval (int): Seconds between checks
        """
        logger.info(f"Starting terminal monitor (check interval: {check_interval}s)")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                closed = self.check_for_closed_windows()

                for window in closed:
                    self.export_closed_window(window)

                time.sleep(check_interval)

        except KeyboardInterrupt:
            logger.info("Terminal monitor stopped")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            sys.exit(1)

    def get_status(self):
        """Get current monitoring status."""
        state = {
            'timestamp': datetime.now().isoformat(),
            'terminal_app_available': self.terminal_app.is_available(),
            'iterm2_available': self.iterm2.is_available(),
            'terminal_app_windows': self.previous_state['terminal_app']['count'],
            'iterm2_windows': self.previous_state['iterm2']['count'],
            'export_directory': str(self.export_manager.export_dir),
            'log_file': str(log_dir / 'terminal_monitor.log')
        }

        return state


def main():
    """CLI interface for terminal monitor."""
    import argparse

    parser = argparse.ArgumentParser(description='Terminal Monitor Daemon')
    parser.add_argument('--start', action='store_true', help='Start monitoring')
    parser.add_argument('--status', action='store_true', help='Show monitoring status')
    parser.add_argument('--check-interval', type=int, default=1, help='Check interval in seconds')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    monitor = TerminalMonitor()

    if args.status:
        status = monitor.get_status()
        print("\n📊 Terminal Monitor Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

    elif args.start:
        if args.verbose:
            logger.setLevel(logging.DEBUG)

        print("\n🚀 Starting Terminal Monitor daemon...")
        print(f"   Check interval: {args.check_interval}s")
        print(f"   Log file: {log_dir / 'terminal_monitor.log'}")
        print("   Press Ctrl+C to stop\n")

        monitor.run(check_interval=args.check_interval)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
