import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import subprocess
from preset_manager import PresetManager
from config import (
    EXCLUDE_DIRS, DEFAULT_TARGET_FILES,
    SUPPORTED_EXTENSIONS, DEFAULT_OUTPUT_DIR
)
from main import generate_summary

def main():
    window = tk.Tk()
    window.title("Project Summary Generator")
    window.geometry("820x450")

    preset_manager = PresetManager()

    def pick_root_dir():
        initial_dir = os.path.expanduser("~")  # ユーザーのホームディレクトリを取得
        result = filedialog.askdirectory(initialdir=initial_dir)
        if result:
            root_dir.set(result)
            load_preset(result)

    def pick_output_dir():
        initial_dir = os.path.expanduser("~")  # ユーザーのホームディレクトリを取得
        result = filedialog.askdirectory(initialdir=initial_dir)
        if result:
            output_dir.set(result)

    def load_preset(directory):
        preset_data = preset_manager.load_preset(directory)
        if preset_data:
            exclude_dirs.set(preset_data.get('exclude_dirs', exclude_dirs.get()))
            output_dir.set(preset_data.get('output_dir', output_dir.get()))
            target_files.set(preset_data.get('target_files', target_files.get()))
            preset_extensions = preset_data.get('include_extensions', [])
            for ext, var in extension_vars.items():
                var.set(ext in preset_extensions)

    root_dir = tk.StringVar()
    exclude_dirs = tk.StringVar(value=", ".join(EXCLUDE_DIRS))
    output_dir = tk.StringVar(value=DEFAULT_OUTPUT_DIR)
    target_files = tk.StringVar(value=", ".join(DEFAULT_TARGET_FILES))

    extension_vars = {ext: tk.BooleanVar(value=ext in [".md", ".py"]) for ext in SUPPORTED_EXTENSIONS}

    ttk.Label(window, text="ルートディレクトリ:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=root_dir, width=50, state="readonly").grid(row=0, column=1, padx=10, pady=5)
    ttk.Button(window, text="参照", command=pick_root_dir).grid(row=0, column=2, padx=10, pady=5)

    ttk.Label(window, text="除外ディレクトリ (カンマ区切り):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=exclude_dirs, width=50).grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(window, text="含める拡張子:").grid(row=2, column=0, sticky=tk.NW, padx=10, pady=5)
    extension_frame = ttk.Frame(window)
    extension_frame.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
    for i, ext in enumerate(SUPPORTED_EXTENSIONS):
        ttk.Checkbutton(extension_frame, text=ext, variable=extension_vars[ext]).grid(row=i//5, column=i%5, sticky=tk.W, padx=5, pady=2)

    ttk.Label(window, text="出力ディレクトリ:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=output_dir, width=50, state="readonly").grid(row=3, column=1, padx=10, pady=5)
    ttk.Button(window, text="参照", command=pick_output_dir).grid(row=3, column=2, padx=10, pady=5)

    ttk.Label(window, text="対象ファイル (カンマ区切り):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=target_files, width=50).grid(row=4, column=1, padx=10, pady=5)

    def open_output_directory(path):
        if os.path.exists(path):
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(('open', path))
        else:
            messagebox.showerror("エラー", f"ディレクトリが見つかりません：\n{path}")

    def generate_summary_callback():
        if not root_dir.get():
            messagebox.showerror("エラー", "ルートディレクトリを選択してください。")
            return

        selected_extensions = [ext for ext, var in extension_vars.items() if var.get()]
        output_filename = os.path.basename(root_dir.get()) + ".md"

        # プリセットの保存
        preset_data = {
            'exclude_dirs': exclude_dirs.get(),
            'include_extensions': selected_extensions,
            'output_dir': output_dir.get(),
            'target_files': target_files.get()
        }
        preset_manager.save_preset(root_dir.get(), preset_data)

        try:
            generate_summary(
                root_dir.get(),
                [dir.strip() for dir in exclude_dirs.get().split(",")],
                selected_extensions,
                output_filename,
                output_dir.get(),
                [file.strip() for file in target_files.get().split(",")]
            )
            messagebox.showinfo("成功", f"サマリーが生成されました。\n保存先: {os.path.join(output_dir.get(), output_filename)}")
            open_output_directory(output_dir.get())
        except Exception as e:
            messagebox.showerror("エラー", f"サマリーの生成中にエラーが発生しました：\n{str(e)}")

    ttk.Button(window, text="サマリーを生成", command=generate_summary_callback).grid(row=5, column=1, pady=20)

    window.mainloop()

if __name__ == "__main__":
    main()