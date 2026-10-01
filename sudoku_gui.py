import tkinter as tk
from tkinter import ttk, messagebox
import random

class SudokuAI:
    def __init__(self, size=9, difficulty="Середня"):
        self.size = size
        self.difficulty = difficulty
        
        if size == 6:
            self.block_rows, self.block_cols = 2, 3
            self.symbols = [str(i) for i in range(1, 7)]
        elif size == 9:
            self.block_rows, self.block_cols = 3, 3
            self.symbols = [str(i) for i in range(1, 10)]
        elif size == 16:
            self.block_rows, self.block_cols = 4, 4
            self.symbols = [str(i) for i in range(1, 10)] + ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    def is_valid(self, board, row, col, num):
        for i in range(self.size):
            if board[row][i] == num or board[i][col] == num:
                return False
        
        start_row = self.block_rows * (row // self.block_rows)
        start_col = self.block_cols * (col // self.block_cols)
        for i in range(self.block_rows):
            for j in range(self.block_cols):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def solve(self, board):
        for row in range(self.size):
            for col in range(self.size):
                if board[row][col] == "":
                    numbers = list(self.symbols)
                    random.shuffle(numbers)
                    for num in numbers:
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            if self.solve(board):
                                return True
                            board[row][col] = ""
                    return False
        return True

    def generate_puzzle(self):
        self.board = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.solve(self.board)
        puzzle = [row[:] for row in self.board]
        
        total_cells = self.size * self.size
        if self.difficulty == "Легка": remove_count = int(total_cells * 0.35)
        elif self.difficulty == "Складна": remove_count = int(total_cells * 0.60)
        else: remove_count = int(total_cells * 0.48)
            
        cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        random.shuffle(cells)
        for r, c in cells[:remove_count]:
            puzzle[r][c] = ""
            
        return puzzle, self.board

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Sudoku Generator")
        self.root.resizable(False, False)
        
        self.ai = None
        self.solution = []
        self.entries = []
        self.vars = [] # Зберігаємо змінні для прямого доступу до тексту
        
        self.game_over = False
        self.is_solving = False # Прапорець для ігнорування вводу під час автозаповнення
        self.mistakes = 0
        self.hints = 3
        
        # --- Панель керування ---
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(control_frame, text="Розмір:").pack(side=tk.LEFT)
        self.size_var = tk.StringVar(value="9x9")
        ttk.Combobox(control_frame, textvariable=self.size_var, values=["6x6", "9x9", "16x16"], width=5, state="readonly").pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Складність:").pack(side=tk.LEFT, padx=5)
        self.diff_var = tk.StringVar(value="Середня")
        ttk.Combobox(control_frame, textvariable=self.diff_var, values=["Легка", "Середня", "Складна"], width=10, state="readonly").pack(side=tk.LEFT)
        
        tk.Button(control_frame, text="Нова гра", command=self.generate_board, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
        
        self.hint_btn = tk.Button(control_frame, text="Підказка (3)", command=self.use_hint, bg="#FF9800", fg="white")
        self.hint_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Розв'язок", command=self.show_solution, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        
        self.mistakes_label = tk.Label(control_frame, text="Помилки: 0/3", fg="#F44336", font=('Arial', 10, 'bold'))
        self.mistakes_label.pack(side=tk.RIGHT, padx=5)
        
        self.grid_frame = tk.Frame(root, padx=10, pady=10, bg="black")
        self.grid_frame.pack(side=tk.TOP)
        
        self.generate_board()

    def on_input(self, r, c, sv):
        # Ігноруємо перевірку, якщо масив заповнюється скриптом (розв'язок або підказка)
        if self.is_solving:
            return
            
        val = sv.get().upper()
        
        if self.game_over:
            self.is_solving = True
            sv.set("")
            self.is_solving = False
            return
            
        if not val:
            return
            
        if len(val) > 1:
            val = val[-1]
            self.is_solving = True
            sv.set(val)
            self.is_solving = False
            
        if val not in self.ai.symbols:
            self.is_solving = True
            sv.set("")
            self.is_solving = False
            return
            
        # Логіка перевірки
        if val == self.solution[r][c]:
            self.entries[r][c].config(disabledforeground="#4CAF50", disabledbackground="white", state="disabled")
            self.check_win()
        else:
            self.entries[r][c].config(fg="#F44336")
            self.mistakes += 1
            self.mistakes_label.config(text=f"Помилки: {self.mistakes}/3")
            
            if self.mistakes >= 3:
                self.end_game()

    def use_hint(self):
        if self.hints <= 0 or self.game_over:
            return
            
        # Шукаємо всі клітинки, які ще не мають правильної відповіді
        empty_cells = []
        for r in range(self.ai.size):
            for c in range(self.ai.size):
                if self.vars[r][c].get().upper() != self.solution[r][c]:
                    empty_cells.append((r, c))
                    
        if not empty_cells:
            return
            
        # Обираємо випадкову клітинку
        r, c = random.choice(empty_cells)
        
        # Записуємо туди правильну відповідь.
        # Це автоматично викличе on_input(), зробить її зеленою і заблокує.
        self.vars[r][c].set(self.solution[r][c])
        
        # Оновлюємо лічильник
        self.hints -= 1
        self.hint_btn.config(text=f"Підказка ({self.hints})")
        if self.hints == 0:
            self.hint_btn.config(state="disabled")

    def show_solution(self):
        if not self.solution:
            return
            
        self.is_solving = True
        self.game_over = True
        
        for r in range(self.ai.size):
            for c in range(self.ai.size):
                current_val = self.vars[r][c].get().upper()
                if current_val != self.solution[r][c]:
                    self.entries[r][c].config(state="normal")
                    self.vars[r][c].set(self.solution[r][c])
                    self.entries[r][c].config(state="disabled", disabledforeground="#2196F3", disabledbackground="white")
                    
        self.is_solving = False

    def check_win(self):
        for r in range(self.ai.size):
            for c in range(self.ai.size):
                if self.vars[r][c].get().upper() != self.solution[r][c]:
                    return
        self.game_over = True
        messagebox.showinfo("Перемога!", "Ви успішно розв'язали Судоку!")

    def end_game(self):
        self.game_over = True
        for r in range(self.ai.size):
            for c in range(self.ai.size):
                if self.entries[r][c]['state'] != 'disabled':
                    self.entries[r][c].config(state="disabled")
        messagebox.showerror("Поразка", "Ви зробили 3 помилки - гру закінчено.")

    def generate_board(self):
        size_str = self.size_var.get()
        size = int(size_str.split("x")[0])
        difficulty = self.diff_var.get()
        
        self.ai = SudokuAI(size=size, difficulty=difficulty)
        puzzle, self.solution = self.ai.generate_puzzle()
        
        self.game_over = False
        self.is_solving = False
        self.mistakes = 0
        self.hints = 3
        
        self.mistakes_label.config(text="Помилки: 0/3")
        self.hint_btn.config(text="Підказка (3)", state="normal")
        
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
            
        self.entries = []
        self.vars = []
        
        for r in range(size):
            row_entries = []
            row_vars = []
            for c in range(size):
                pad_bottom = 3 if (r + 1) % self.ai.block_rows == 0 and r != size - 1 else 1
                pad_right = 3 if (c + 1) % self.ai.block_cols == 0 and c != size - 1 else 1
                
                var = tk.StringVar()
                e = tk.Entry(self.grid_frame, textvariable=var, width=2, font=('Arial', 16, 'bold'), justify='center')
                e.grid(row=r, column=c, padx=(1, pad_right), pady=(1, pad_bottom), ipady=5)
                
                if puzzle[r][c] != "":
                    var.set(puzzle[r][c])
                    e.config(state="disabled", disabledforeground="black", disabledbackground="#e0e0e0")
                else:
                    var.trace_add("write", lambda name, index, mode, r=r, c=c, sv=var: self.on_input(r, c, sv))
                
                row_entries.append(e)
                row_vars.append(var)
                
            self.entries.append(row_entries)
            self.vars.append(row_vars)
            
        self.root.geometry("") 
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()