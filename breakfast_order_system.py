import tkinter as tk
from tkinter import ttk, messagebox


class BreakfastOrderSystem:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("早餐店點餐系統")
        self.root.geometry("860x560")
        self.root.minsize(820, 520)

        self.menu_items = [
            {"name": "蛋餅", "price": 35},
            {"name": "火腿蛋吐司", "price": 45},
            {"name": "鐵板麵", "price": 55},
            {"name": "蘿蔔糕", "price": 40},
            {"name": "薯餅", "price": 30},
            {"name": "熱狗", "price": 25},
            {"name": "奶茶", "price": 25},
            {"name": "紅茶", "price": 20},
            {"name": "豆漿", "price": 20},
            {"name": "咖啡", "price": 35},
        ]

        self.item_vars: dict[str, tk.BooleanVar] = {}
        self.qty_vars: dict[str, tk.StringVar] = {}
        self.total_var = tk.StringVar(value="總金額：$0")

        self._build_ui()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)

        left_frame = ttk.LabelFrame(self.root, text="菜單")
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_frame.columnconfigure(0, weight=4)
        left_frame.columnconfigure(1, weight=2)
        left_frame.columnconfigure(2, weight=2)

        ttk.Label(left_frame, text="餐點").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ttk.Label(left_frame, text="單價").grid(row=0, column=1, padx=8, pady=6)
        ttk.Label(left_frame, text="數量").grid(row=0, column=2, padx=8, pady=6)

        for idx, item in enumerate(self.menu_items, start=1):
            name = item["name"]
            price = item["price"]

            selected_var = tk.BooleanVar(value=False)
            qty_var = tk.StringVar(value="0")

            self.item_vars[name] = selected_var
            self.qty_vars[name] = qty_var

            cb = ttk.Checkbutton(
                left_frame,
                text=name,
                variable=selected_var,
                command=self._on_item_toggle,
            )
            cb.grid(row=idx, column=0, padx=8, pady=5, sticky="w")

            ttk.Label(left_frame, text=f"${price}").grid(row=idx, column=1, padx=8, pady=5)

            qty_spin = ttk.Spinbox(
                left_frame,
                from_=0,
                to=20,
                textvariable=qty_var,
                width=6,
                command=self._update_total,
                justify="center",
            )
            qty_spin.grid(row=idx, column=2, padx=8, pady=5)
            qty_spin.bind("<KeyRelease>", lambda _event: self._update_total())
            qty_spin.bind("<FocusOut>", lambda _event: self._normalize_quantity())

        right_frame = ttk.LabelFrame(self.root, text="訂單資訊")
        right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        ttk.Label(
            right_frame,
            text="已選餐點",
            font=("Microsoft JhengHei", 11, "bold"),
        ).grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

        self.order_text = tk.Text(right_frame, height=16, width=36, state="disabled")
        self.order_text.grid(row=1, column=0, padx=10, pady=6, sticky="nsew")

        ttk.Label(
            right_frame,
            textvariable=self.total_var,
            font=("Microsoft JhengHei", 14, "bold"),
            foreground="#1144aa",
        ).grid(row=2, column=0, padx=10, pady=10, sticky="e")

        btn_frame = ttk.Frame(right_frame)
        btn_frame.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        btn_frame.columnconfigure((0, 1, 2), weight=1)

        ttk.Button(btn_frame, text="更新明細", command=self._refresh_order_details).grid(
            row=0, column=0, padx=4, pady=4, sticky="ew"
        )
        ttk.Button(btn_frame, text="清空", command=self._clear_order).grid(
            row=0, column=1, padx=4, pady=4, sticky="ew"
        )
        ttk.Button(btn_frame, text="結帳", command=self._checkout).grid(
            row=0, column=2, padx=4, pady=4, sticky="ew"
        )

        self._update_total()
        self._refresh_order_details()

    def _parse_qty(self, text: str) -> int:
        try:
            qty = int(text)
        except ValueError:
            return 0
        return max(0, min(qty, 20))

    def _normalize_quantity(self) -> None:
        for name, qty_var in self.qty_vars.items():
            qty = self._parse_qty(qty_var.get())
            qty_var.set(str(qty))
            if qty == 0 and self.item_vars[name].get():
                self.item_vars[name].set(False)
        self._update_total()
        self._refresh_order_details()

    def _on_item_toggle(self) -> None:
        for name, selected_var in self.item_vars.items():
            if selected_var.get() and self._parse_qty(self.qty_vars[name].get()) == 0:
                self.qty_vars[name].set("1")
            elif not selected_var.get():
                self.qty_vars[name].set("0")
        self._update_total()
        self._refresh_order_details()

    def _collect_order(self) -> tuple[list[tuple[str, int, int]], int]:
        details: list[tuple[str, int, int]] = []
        total = 0
        for item in self.menu_items:
            name = item["name"]
            price = item["price"]
            qty = self._parse_qty(self.qty_vars[name].get())
            selected = self.item_vars[name].get()
            if selected and qty > 0:
                subtotal = price * qty
                details.append((name, qty, subtotal))
                total += subtotal
        return details, total

    def _update_total(self) -> None:
        details, total = self._collect_order()
        # Keep checkbox status consistent with quantity during direct input.
        selected_names = {name for name, _, _ in details}
        for item in self.menu_items:
            name = item["name"]
            self.item_vars[name].set(name in selected_names)
        self.total_var.set(f"總金額：${total}")

    def _refresh_order_details(self) -> None:
        details, total = self._collect_order()

        self.order_text.config(state="normal")
        self.order_text.delete("1.0", "end")
        if not details:
            self.order_text.insert("end", "目前尚未選擇餐點。\n")
        else:
            for name, qty, subtotal in details:
                self.order_text.insert("end", f"{name} x {qty:<2}  小計 ${subtotal}\n")
            self.order_text.insert("end", "-" * 26 + "\n")
            self.order_text.insert("end", f"總計：${total}\n")
        self.order_text.config(state="disabled")

    def _clear_order(self) -> None:
        for name in self.item_vars:
            self.item_vars[name].set(False)
            self.qty_vars[name].set("0")
        self._update_total()
        self._refresh_order_details()

    def _checkout(self) -> None:
        self._normalize_quantity()
        details, total = self._collect_order()
        if not details:
            messagebox.showwarning("提醒", "請先選擇至少一項餐點。")
            return

        summary = "\n".join([f"{name} x {qty} = ${subtotal}" for name, qty, subtotal in details])
        messagebox.showinfo(
            "結帳完成",
            f"訂單如下：\n\n{summary}\n\n總金額：${total}\n\n謝謝光臨！",
        )
        self._clear_order()


def main() -> None:
    root = tk.Tk()
    app = BreakfastOrderSystem(root)
    root.mainloop()


if __name__ == "__main__":
    main()
