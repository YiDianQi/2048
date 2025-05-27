import tkinter as tk
from tkinter import messagebox
import random
import json


class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title("2048游戏")
        self.root.bind("<Key>", self.handle_key_press)

        # 游戏配置
        self.size = 4
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.high_score = self.load_high_score()

        # 颜色映射（可替换为图片路径）
        self.colors = {
            0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
            16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
            256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e"
        }

        # 创建界面组件
        self.create_widgets()
        self.reset_game()  # 初始化游戏状态

    def create_widgets(self):
        # 标题和得分区域
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="2048游戏", font=("Arial", 24, "bold")).pack(side=tk.LEFT)

        # 得分显示框
        score_frame = tk.Frame(top_frame, bg="#bbada0", padx=10, pady=5, borderwidth=2, relief=tk.RIDGE)
        score_frame.pack(side=tk.RIGHT, padx=20)
        tk.Label(score_frame, text="得分", fg="white", bg="#bbada0").pack()
        self.score_label = tk.Label(score_frame, text="0", fg="white", bg="#bbada0", font=("Arial", 14, "bold"))
        self.score_label.pack()

        # 最高分显示框
        high_score_frame = tk.Frame(top_frame, bg="#bbada0", padx=10, pady=5, borderwidth=2, relief=tk.RIDGE)
        high_score_frame.pack(side=tk.RIGHT)
        tk.Label(high_score_frame, text="最高分", fg="white", bg="#bbada0").pack()
        self.high_score_label = tk.Label(high_score_frame, text=str(self.high_score), fg="white", bg="#bbada0",
                                         font=("Arial", 14, "bold"))
        self.high_score_label.pack()

        # 游戏板区域
        self.board_frame = tk.Frame(self.root, bg="#bbada0", padx=10, pady=10)
        self.board_frame.pack()

        # 初始化单元格
        self.cells = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                cell = tk.Frame(self.board_frame, width=100, height=100, bg="#cdc1b4", borderwidth=2, relief=tk.GROOVE)
                cell.grid(row=i, column=j, padx=5, pady=5)
                row.append(cell)
            self.cells.append(row)

        # 规则说明
        tk.Label(self.root, text="游戏规则：使用方向键（上、下、左、右）控制方块移动，相同数字的方块会合并，目标是合并出2048！",
                 wraplength=400).pack(pady=10)

    def update_board_display(self):
        """更新游戏板显示"""
        for i in range(self.size):
            for j in range(self.size):
                value = self.board[i][j]
                cell = self.cells[i][j]
                cell.config(bg=self.colors.get(value, "#cdc1b4"))

                # 清除旧内容并添加新数字
                for widget in cell.winfo_children():
                    widget.destroy()
                if value != 0:
                    tk.Label(cell, text=str(value),
                             font=("Arial", 24, "bold"),
                             fg="black" if value <= 4 else "white",
                             bg=self.colors[value]).pack(expand=True)

        # 更新得分显示
        self.score_label.config(text=str(self.score))
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_label.config(text=str(self.high_score))
            self.save_high_score()

    def add_random_tile(self):
        """随机生成新方块（2或4）"""
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.board[i][j] = 2 if random.random() < 0.9 else 4

    def merge_tiles(self, row):
        """核心合并逻辑（修复关键错误）"""
        merged = []
        prev = None
        for num in row:
            if num == 0:
                continue
            if prev is None:
                prev = num
            elif prev == num:
                new_value = prev * 2
                merged.append(new_value)
                self.score += new_value
                if new_value == 2048:  # 修复：在合并时检查新值
                    messagebox.showinfo("胜利", "恭喜你合并出了2048！")
                prev = None  # 合并后重置prev
            else:
                merged.append(prev)
                prev = num
        if prev is not None:
            merged.append(prev)
        # 补0到4格
        return merged + [0] * (self.size - len(merged))

    def move_left(self):
        """向左移动"""
        changed = False
        for i in range(self.size):
            original_row = self.board[i].copy()
            self.board[i] = self.merge_tiles(self.board[i])
            if self.board[i] != original_row:
                changed = True
        if changed:
            self.add_random_tile()

    def move_right(self):
        """向右移动"""
        changed = False
        for i in range(self.size):
            original_row = self.board[i].copy()
            reversed_row = list(reversed(self.board[i]))
            merged_row = self.merge_tiles(reversed_row)
            self.board[i] = list(reversed(merged_row))
            if self.board[i] != original_row:
                changed = True
        if changed:
            self.add_random_tile()

    def move_up(self):
        """向上移动"""
        changed = False
        for j in range(self.size):
            column = [self.board[i][j] for i in range(self.size)]
            original_col = column.copy()
            merged_col = self.merge_tiles(column)
            for i in range(self.size):
                self.board[i][j] = merged_col[i]
            if merged_col != original_col:
                changed = True
        if changed:
            self.add_random_tile()

    def move_down(self):
        """向下移动"""
        changed = False
        for j in range(self.size):
            column = [self.board[i][j] for i in range(self.size)]
            original_col = column.copy()
            reversed_col = list(reversed(column))
            merged_col = self.merge_tiles(reversed_col)
            new_col = list(reversed(merged_col))
            for i in range(self.size):
                self.board[i][j] = new_col[i]
            if new_col != original_col:
                changed = True
        if changed:
            self.add_random_tile()

    def handle_key_press(self, event):
        """处理键盘事件"""
        original_state = [row.copy() for row in self.board]
        original_score = self.score

        if event.keysym in ("Left", "Right", "Up", "Down"):
            {
                "Left": self.move_left,
                "Right": self.move_right,
                "Up": self.move_up,
                "Down": self.move_down
            }[event.keysym]()

        # 状态变化后更新显示
        if [row.copy() for row in self.board] != original_state or self.score != original_score:
            self.update_board_display()
            self.check_game_over()

    def check_game_over(self):
        """检查游戏是否结束"""
        if any(0 in row for row in self.board):
            return  # 还有空位

        # 检查是否有可合并的方块
        for i in range(self.size):
            for j in range(self.size):
                current = self.board[i][j]
                if (j < self.size - 1 and current == self.board[i][j + 1]) or \
                        (i < self.size - 1 and current == self.board[i + 1][j]):
                    return  # 还有可合并的

        # 游戏结束提示
        result = messagebox.askyesno("游戏结束", f"最终得分：{self.score}\n是否重新开始？")
        if result:
            self.reset_game()
        else:
            self.root.destroy()

    def reset_game(self):
        """重置游戏状态"""
        self.board = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.add_random_tile()
        self.add_random_tile()
        self.update_board_display()

    def load_high_score(self):
        """加载历史最高分"""
        try:
            with open("high_score.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def save_high_score(self):
        """保存历史最高分"""
        with open("high_score.json", "w") as f:
            json.dump(self.high_score, f)


if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop()