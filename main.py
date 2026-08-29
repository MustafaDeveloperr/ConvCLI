#!/usr/bin/env python3
import os
import sys
import stat
import shutil
from pathlib import Path
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()

class ModernFileManager:
    def __init__(self):
        self.current_path = Path.cwd().resolve()
        self.selected_idx = 0
        self.show_hidden = False
        self.clipboard = None
        self.is_cut = False
        self.status_message = "Welcome to Modern File Manager CLI!"
        self.status_style = "green"

    def get_items(self):
        items = []
        try:
            for p in self.current_path.iterdir():
                if not self.show_hidden and p.name.startswith('.'):
                    continue
                
                is_symlink = p.is_symlink()
                try:
                    st = p.stat()
                except FileNotFoundError:
                    st = p.lstat()
                
                is_dir = stat.S_ISDIR(st.st_mode)
                is_exec = not is_dir and (st.st_mode & 0o111 != 0)
                perms = stat.filemode(p.lstat().st_mode)
                size = st.st_size if not is_dir else 0
                
                items.append({
                    'name': p.name,
                    'path': p,
                    'is_dir': is_dir,
                    'is_symlink': is_symlink,
                    'is_exec': is_exec,
                    'perms': perms,
                    'size': size
                })
        except PermissionError:
            self.set_status("Permission denied to read this folder.", "red")
            
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        return items

    def set_status(self, msg, style="cyan"):
        self.status_message = msg
        self.status_style = style

    def render_ui(self):
        console.clear()
        items = self.get_items()
        
        if self.selected_idx >= len(items) and items:
            self.selected_idx = len(items) - 1
        elif not items:
            self.selected_idx = 0

        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        clip_info = f" | [yellow]Clipboard: {self.clipboard.name} ({'CUT' if self.is_cut else 'COPY'})[/yellow]" if self.clipboard else ""
        header_text = Text(f" 📂 Path: {self.current_path}{clip_info}", style="bold cyan")
        layout["header"].update(Panel(header_text, border_style="cyan"))

        table = Table(show_header=True, header_style="bold magenta", expand=True, box=None)
        table.add_column("Type", width=6, justify="center")
        table.add_column("Name", ratio=3)
        table.add_column("Permissions", width=12)
        table.add_column("Size", width=10, justify="right")

        for idx, item in enumerate(items):
            if item['is_symlink']:
                icon, style = "🔗", "magenta"
            elif item['is_dir']:
                icon, style = "📁", "bold blue"
            elif item['is_exec']:
                icon, style = "⚙️", "bold green"
            else:
                icon, style = "📄", "white"

            name_str = item['name']
            size_str = f"{item['size']} B" if item['size'] < 1024 else f"{item['size']//1024} KB"

            row_style = "reverse bold" if idx == self.selected_idx else style
            table.add_row(icon, name_str, item['perms'], size_str, style=row_style)

        layout["body"].update(Panel(table, title=" [bold]Explorer[/bold] ", border_style="blue"))

        footer_text = Text(" ↑↓/j/k: Navigate | Enter: Open | Backspace: Up | n: New | r: Rename | d: Delete | c: Copy | m: Cut | p: Paste | h: Hidden | q: Quit ", style="dim white")
        layout["footer"].update(Panel(footer_text, border_style="cyan"))

        console.print(layout)
        console.print(f"[{self.status_style}]{self.status_message}[/{self.status_style}]")

    def run(self):
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            while True:
                self.render_ui()
                ch = sys.stdin.read(1)
                
                if ch == 'q':
                    break
                elif ch == 'h':
                    self.show_hidden = not self.show_hidden
                    status_text = "On" if self.show_hidden else "Off"
                    self.set_status(f"Hidden files: {status_text}")
                elif ch == 'j' or ch == '\x1b[B':
                    items = self.get_items()
                    if self.selected_idx < len(items) - 1:
                        self.selected_idx += 1
                elif ch == 'k' or ch == '\x1b[A':
                    if self.selected_idx > 0:
                        self.selected_idx -= 1
                elif ch == '\n':
                    items = self.get_items()
                    if items:
                        selected = items[self.selected_idx]
                        if selected['is_dir']:
                            try:
                                self.current_path = selected['path'].resolve()
                                self.selected_idx = 0
                                self.set_status(f"Opened: {self.current_path.name}")
                            except PermissionError:
                                self.set_status("Permission Denied!", "red")
                elif ch == '\x7f' or ch == '\b':
                    self.current_path = self.current_path.parent
                    self.selected_idx = 0
                    self.set_status(f"Moved up to {self.current_path.name}")
                elif ch == 'n':
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    name = Prompt.ask("\n[bold green]Enter name (end with / for folder)[/bold green]")
                    tty.setcbreak(fd)
                    if name:
                        target = self.current_path / name.rstrip('/')
                        try:
                            if name.endswith('/'):
                                target.mkdir(parents=True, exist_ok=True)
                            else:
                                target.touch()
                            self.set_status(f"Created: {name}", "green")
                        except Exception as e:
                            self.set_status(f"Error: {e}", "red")
                elif ch == 'd':
                    items = self.get_items()
                    if items:
                        selected = items[self.selected_idx]
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        confirm = Confirm.ask(f"\n[bold red]Delete {selected['name']}?[/bold red]")
                        tty.setcbreak(fd)
                        if confirm:
                            try:
                                if selected['path'].is_dir() and not selected['path'].is_symlink():
                                    shutil.rmtree(selected['path'])
                                else:
                                    selected['path'].unlink()
                                self.set_status(f"Deleted: {selected['name']}", "yellow")
                            except Exception as e:
                                self.set_status(f"Error: {e}", "red")
                elif ch == 'c':
                    items = self.get_items()
                    if items:
                        self.clipboard = items[self.selected_idx]['path']
                        self.is_cut = False
                        self.set_status(f"Copied to clipboard: {self.clipboard.name}", "blue")
                elif ch == 'm':
                    items = self.get_items()
                    if items:
                        self.clipboard = items[self.selected_idx]['path']
                        self.is_cut = True
                        self.set_status(f"Cut to clipboard: {self.clipboard.name}", "blue")
                elif ch == 'p':
                    if self.clipboard and self.clipboard.exists():
                        target = self.current_path / self.clipboard.name
                        try:
                            if self.is_cut:
                                shutil.move(str(self.clipboard), str(target))
                                self.clipboard = None
                                self.set_status("Moved successfully!", "green")
                            else:
                                if self.clipboard.is_dir():
                                    shutil.copytree(self.clipboard, target)
                                else:
                                    shutil.copy2(self.clipboard, target)
                                self.set_status("Copied successfully!", "green")
                        except Exception as e:
                            self.set_status(f"Error: {e}", "red")

        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            console.clear()

if __name__ == "__main__":
    app = ModernFileManager()
    app.run()