import cv2
import numpy as np
from PIL import Image, ImageTk
from openpyxl import Workbook, load_workbook
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import fitz  # PyMuPDF

# =========================
# CONFIG
# =========================
excel_path = r"D:\AI_CODING\PYTHON\project1\Quote_Generator\Quote_Book.xlsx"

SCALE = 0.3
CM_PER_PIXEL = 2.54 / (300 * SCALE)

# =========================
# GLOBAL STATE
# =========================
img_cv = None
img_display = None
canvas_img = None

history_stack = []
redo_stack = []

start_x, start_y = 0, 0
dragging = False

selected_ids = set()

pdf_doc = None
page_index = 0
total_pages = 0

current_file_path = None   # ✅ NEW

# =========================
# FILE OPEN
# =========================
def open_file():
    global current_file_path

    file_path = filedialog.askopenfilename(
        filetypes=[
            ("All Supported", "*.png *.jpg *.jpeg *.pdf"),
            ("Images", "*.png *.jpg *.jpeg"),
            ("PDF", "*.pdf")
        ]
    )

    if not file_path:
        return

    current_file_path = file_path  # ✅ store file path

    if file_path.lower().endswith(".pdf"):
        load_pdf(file_path)
    else:
        load_image(file_path)

# =========================
# LOAD IMAGE
# =========================
def load_image(path):
    global img_cv, img_display, history_stack, redo_stack, selected_ids, pdf_doc

    pdf_doc = None

    img = Image.open(path).convert("RGB")
    img = np.array(img)

    img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_cv = cv2.resize(img_cv, (0, 0), fx=SCALE, fy=SCALE)

    img_display = img_cv.copy()

    history_stack.clear()
    redo_stack.clear()
    selected_ids.clear()

    redraw()

# =========================
# PDF HANDLING
# =========================
def load_pdf(path):
    global pdf_doc, page_index, total_pages

    pdf_doc = fitz.open(path)
    total_pages = len(pdf_doc)
    page_index = 0

    load_pdf_page(page_index)


def load_pdf_page(index):
    global img_cv, img_display, history_stack, redo_stack, page_index

    page_index = index
    page = pdf_doc.load_page(page_index)

    pix = page.get_pixmap(dpi=300)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img_cv = cv2.resize(img_cv, (0, 0), fx=SCALE, fy=SCALE)

    img_display = img_cv.copy()

    history_stack.clear()
    redo_stack.clear()
    selected_ids.clear()

    redraw()

    print(f"📄 Page {page_index + 1}/{total_pages}")

# =========================
# OBJECT DETECTION
# =========================
def get_objects(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 245, 255, cv2.THRESH_BINARY_INV)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    objects = []
    for i, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        if w > 5 and h > 5:
            objects.append((i, x, y, x + w, y + h))

    return objects

# =========================
# PROCESS AREA
# =========================
def process_area(x1, y1, x2, y2):
    global history_stack, redo_stack, selected_ids

    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    objects = get_objects(img_cv)

    selected = []
    obj_ids = set()

    for obj_id, bx1, by1, bx2, by2 in objects:

        if obj_id in selected_ids:
            continue

        if bx1 >= x1 and by1 >= y1 and bx2 <= x2 and by2 <= y2:
            selected.append((bx1, by1, bx2, by2))
            obj_ids.add(obj_id)

    if not selected:
        print("❌ No new objects selected")
        return

    selected_ids.update(obj_ids)

    xs, ys = [], []
    for bx1, by1, bx2, by2 in selected:
        xs += [bx1, bx2]
        ys += [by1, by2]

    history_stack.append(((min(xs), min(ys), max(xs), max(ys)), obj_ids))
    redo_stack.clear()

    redraw()

# =========================
# REDRAW
# =========================
def redraw():
    global img_display

    img_display = img_cv.copy()

    for (box, _) in history_stack:
        x1, y1, x2, y2 = box
        cv2.rectangle(img_display, (x1, y1), (x2, y2), (0, 0, 255), 2)

    draw_image()

# =========================
# DRAW IMAGE
# =========================
def draw_image():
    global canvas_img

    if img_display is None:
        return

    img_rgb = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)

    img_pil = img_pil.resize((canvas.winfo_width(), canvas.winfo_height()))

    canvas_img = ImageTk.PhotoImage(img_pil)
    canvas.create_image(0, 0, anchor="nw", image=canvas_img)

# =========================
# PREVIEW BOX
# =========================
def preview(x, y):
    temp = img_display.copy()

    cv2.rectangle(temp, (start_x, start_y), (x, y), (0, 255, 0), 2)

    img_rgb = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)

    img_pil = img_pil.resize((canvas.winfo_width(), canvas.winfo_height()))

    global canvas_img
    canvas_img = ImageTk.PhotoImage(img_pil)
    canvas.create_image(0, 0, anchor="nw", image=canvas_img)

# =========================
# MOUSE EVENTS
# =========================
def on_mouse(event):
    global start_x, start_y, dragging

    if img_cv is None:
        return

    x = int(event.x * img_cv.shape[1] / canvas.winfo_width())
    y = int(event.y * img_cv.shape[0] / canvas.winfo_height())

    if event.type == "4":
        start_x, start_y = x, y
        dragging = True

    elif event.type == "6" and dragging:
        preview(x, y)

    elif event.type == "5":
        dragging = False
        before = len(history_stack)

        process_area(start_x, start_y, x, y)

        if len(history_stack) == before:
            redraw()

# =========================
# UNDO / REDO
# =========================
def undo():
    global selected_ids

    if history_stack:
        box, obj_ids = history_stack.pop()
        redo_stack.append((box, obj_ids))

        selected_ids.difference_update(obj_ids)
        redraw()

def redo():
    global selected_ids

    if redo_stack:
        box, obj_ids = redo_stack.pop()
        history_stack.append((box, obj_ids))

        selected_ids.update(obj_ids)
        redraw()

# =========================
# SAVE
# =========================
def save_all():
    global page_index, img_cv

    # =========================
    # FILE PATH SETUP
    # =========================
    if current_file_path:
        base_name = os.path.splitext(os.path.basename(current_file_path))[0]
        base_dir = os.path.dirname(current_file_path)

        excel_file = os.path.join(base_dir, f"{base_name}.xlsx")
        output_folder = os.path.join(base_dir, "output_images")
        os.makedirs(output_folder, exist_ok=True)
    else:
        excel_file = excel_path
        output_folder = "."

    wb = load_workbook(excel_file) if os.path.exists(excel_file) else Workbook()
    ws = wb.active

    # =========================
    # HEADER
    # =========================
    if ws.max_row == 1:
        ws.append(["Date", "Page", "H", "W", "Area"])

    page_label = f"color {page_index + 1}"

    # =========================
    # WRITE EXCEL DATA
    # =========================
    for (box, _) in history_stack:
        x1, y1, x2, y2 = box

        w = x2 - x1
        h = y2 - y1

        h_cm = round(h * CM_PER_PIXEL)
        w_cm = round(w * CM_PER_PIXEL)
        area = round(h_cm * w_cm)

        ws.append([
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            page_label,
            h_cm,
            w_cm,
            area
        ])

    wb.save(excel_file)
    print(f"✔ Excel saved -> {excel_file} (Page {page_index + 1})")

    # =========================
    # EXPORT IMAGE WITH RED BOXES
    # =========================
    if img_display is not None:
        img_out = cv2.resize(
            img_display.copy(),
            (img_display.shape[1], img_display.shape[0])
        )

        image_path = os.path.join(
            output_folder,
            f"{os.path.splitext(os.path.basename(current_file_path))[0]}_page_{page_index + 1}.png"
        )

        cv2.imwrite(image_path, img_out)
        print(f"🖼 Image saved (with red boxes) -> {image_path}")

    # =========================
    # RESET SELECTIONS
    # =========================
    history_stack.clear()
    selected_ids.clear()

    # =========================
    # NEXT PAGE HANDLING
    # =========================
    if pdf_doc and page_index + 1 < total_pages:
        load_pdf_page(page_index + 1)
    else:
        print("🎉 All pages completed")
        if pdf_doc:
            pdf_doc.close()
        canvas.delete("all")
        img_cv = None

# =========================
# UI
# =========================
root = tk.Tk()
root.title("PDF/Image Object Selector")
root.state("zoomed")

left = tk.Frame(root, width=75, bg="#007B85")
left.pack(side="left", fill="y")
left.pack_propagate(False)

tk.Button(left, text="Open", font=("Arial", 13), command=open_file).pack(pady=10)
tk.Button(left, text="Undo", font=("Arial", 13), command=undo).pack(pady=10)
tk.Button(left, text="Redo", font=("Arial", 13), command=redo).pack(pady=10)
tk.Button(left, text="Save", font=("Arial", 13), command=save_all, bg="green", fg="white").pack(pady=20)

canvas = tk.Canvas(
    root,
    bg="#EBEBEB",
    highlightthickness=10,
    highlightbackground="#BDBDBD"
)
canvas.pack(side="right", fill="both", expand=True)

canvas.bind("<Button-1>", on_mouse)
canvas.bind("<B1-Motion>", on_mouse)
canvas.bind("<ButtonRelease-1>", on_mouse)

root.mainloop()
