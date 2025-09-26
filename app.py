from flask import Flask, request, render_template_string, send_from_directory
import os

app = Flask(__name__)

# --- HTML шаблон страницы с результатом ---
RESULT_PAGE = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Результат — Калькулятор матриц</title>
  <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
  <main class="card">
    <h1>Результат</h1>
    <section>
      <strong>Операция:</strong> {{op}}<br>
      {% if err %}
        <div style="color:#b91c1c;margin-top:10px;"><strong>Ошибка:</strong> {{err}}</div>
      {% else %}
        <pre style="margin-top:12px;">{{result_text}}</pre>
      {% endif %}
    </section>

    <div style="margin-top:14px;">
      <a href="/" style="text-decoration:none;"><button class="btn muted">Вернуться</button></a>
    </div>
  </main>
</body>
</html>
"""

# --- Маршрут для главной страницы ---
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")


# ---------- вспомогательные функции ----------
def parse_matrix(text):
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip() != ""]
    if not lines:
        return []
    mat = []
    row_len = None
    for i, ln in enumerate(lines):
        parts = ln.replace(',', '.').split()
        row = []
        for p in parts:
            try:
                row.append(float(p))
            except:
                raise ValueError(f"Неправильный элемент в строке {i+1}: '{p}'")
        if row_len is None:
            row_len = len(row)
        elif len(row) != row_len:
            raise ValueError(f"Строки разной длины (строка {i+1})")
        mat.append(row)
    return mat

def shape(m):
    return (len(m), len(m[0]) if m and m[0] else 0)

def add(A,B):
    r,c = shape(A)
    return [[A[i][j]+B[i][j] for j in range(c)] for i in range(r)]

def sub(A,B):
    r,c = shape(A)
    return [[A[i][j]-B[i][j] for j in range(c)] for i in range(r)]

def mul(A,B):
    r1,c1 = shape(A)
    r2,c2 = shape(B)
    if c1 != r2:
        raise ValueError("Число столбцов A должно равняться числу строк B для умножения")
    C = [[0.0]*c2 for _ in range(r1)]
    for i in range(r1):
        for j in range(c2):
            s = 0.0
            for k in range(c1):
                s += A[i][k]*B[k][j]
            C[i][j] = s
    return C

def transpose(A):
    r,c = shape(A)
    return [[A[i][j] for i in range(r)] for j in range(c)]

def det(A):
    n,_ = shape(A)
    if n == 0:
        raise ValueError("Пустая матрица")
    if n != shape(A)[1]:
        raise ValueError("Определитель возможен только для квадратной матрицы")
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0]*A[1][1] - A[0][1]*A[1][0]
    res = 0.0
    for col in range(n):
        minor = []
        for i in range(1, n):
            row = []
            for j in range(n):
                if j == col: continue
                row.append(A[i][j])
            minor.append(row)
        res += ((-1)**col) * A[0][col] * det(minor)
    return res

def inverse(A):
    n,_ = shape(A)
    if n != shape(A)[1]:
        raise ValueError("Обратная возможна только для квадратной матрицы")
    M = [row[:] for row in A]
    I = [[float(i==j) for j in range(n)] for i in range(n)]
    for i in range(n):
        pivot = M[i][i]
        if abs(pivot) < 1e-12:
            swap_row = None
            for r in range(i+1, n):
                if abs(M[r][i]) > 1e-12:
                    swap_row = r
                    break
            if swap_row is None:
                raise ValueError("Матрица вырождена (нет обратной)")
            M[i], M[swap_row] = M[swap_row], M[i]
            I[i], I[swap_row] = I[swap_row], I[i]
            pivot = M[i][i]
        factor = pivot
        M[i] = [v/factor for v in M[i]]
        I[i] = [v/factor for v in I[i]]
        for r in range(n):
            if r == i: continue
            coef = M[r][i]
            if abs(coef) < 1e-15: continue
              M[r] = [M[r][c] - coef*M[i][c] for c in range(n)]
            I[r] = [I[r][c] - coef*I[i][c] for c in range(n)]
    return I

def mat_to_text(M):
    if isinstance(M, (int,float)):
        return str(float(M))
    if not M:
        return "(пусто)"
    lines = []
    for row in M:
        lines.append("  ".join(f"{v:.6g}" for v in row))
    return "\n".join(lines)


# --- Маршрут для вычислений ---
@app.route("/compute", methods=["POST"])
def compute():
    a_text = request.form.get("matrix_a", "")
    b_text = request.form.get("matrix_b", "")
    op = request.form.get("operation", "add")
    err = None
    result_text = ""
    try:
        A = parse_matrix(a_text) if a_text.strip() else []
        B = parse_matrix(b_text) if b_text.strip() else []
        if op in ("add","sub","mul"):
            if not A or not B:
                raise ValueError("Нужны обе матрицы A и B")
            if op == "add":
                if shape(A) != shape(B):
                    raise ValueError("Для сложения размеры должны совпадать")
                result_text = mat_to_text(add(A,B))
            elif op == "sub":
                if shape(A) != shape(B):
                    raise ValueError("Для вычитания размеры должны совпадать")
                result_text = mat_to_text(sub(A,B))
            else:
                result_text = mat_to_text(mul(A,B))
        else:
            if not A:
                raise ValueError("Матрица A пуста")
            if op == "transpose":
                result_text = mat_to_text(transpose(A))
            elif op == "det":
                d = det(A)
                if abs(d - round(d)) < 1e-9:
                    d = round(d)
                result_text = str(d)
            elif op == "inverse":
                result_text = mat_to_text(inverse(A))
            else:
                raise ValueError("Неизвестная операция")
    except Exception as e:
        err = str(e)
    return render_template_string(RESULT_PAGE, op=op, err=err, result_text=result_text)


if __name__ == "__main__":
    app.run(debug=True)
