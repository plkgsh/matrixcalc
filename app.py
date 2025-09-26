from flask import Flask, request, render_template_string, redirect, url_for
import math
app = Flask(__name__)

# -- HTML шаблон результатов (встроен) --
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

# ---------- вспомогательные функции для матриц ----------
def parse_matrix(text):
    """
    Парсит текст в матрицу (list of lists of floats).
    Формат: строки через \n, элементы через пробел.
    """
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
            if row_len == 0:
                raise ValueError("Пустая строка в матрице")
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
    # вычисляем рекурсивно (на маленьких матрицах нормально)
    if n == 1:
        return A[0][0]
    if n == 2:
        return A[0][0]*A[1][1] - A[0][1]*A[1][0]
    res = 0.0
    for col in range(n):
        # построим минор
        minor = []
        for i in range(1, n):
            row = []
            for j in range(n):
                if j == col: continue
                row.append(A[i][j])
            minor.append(row)
        co = ((-1)**col) * A[0][col] * det(minor)
        res += co
    return res

def inverse(A):
    n,_ = shape(A)
    if n != shape(A)[1]:
        raise ValueError("Обратная возможна только для квадратной матрицы")
    # создаём расширенную матрицу [A | I]
    # копируем
    M = [row[:] for row in A]
    I = [[float(i==j) for j in range(n)] for i in range(n)]
    # Прямой ход (Gauss-Jordan)
    for i in range(n):
        # найдем опорный элемент
        pivot = M[i][i]
        if abs(pivot) < 1e-12:
            # попробуем поменять местами с нижней строкой
            swap_row = None
            for r in range(i+1, n):
                if abs(M[r][i]) > 1e-12:
                    swap_row = r
                    break
            if swap_row is None:
                raise ValueError("Матрица вырождена (нет обратной)")
            # swap
            M[i], M[swap_row] = M[swap_row], M[i]
            I[i], I[swap_row] = I[swap_row], I[i]
            pivot = M[i][i]
        # нормализация строки i
        factor = pivot
        M[i] = [v/factor for v in M[i]]
        I[i] = [v/factor for v in I[i]]
        # зануление других строк
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

# ---------- web маршруты ----------
@app.route("/", methods=["GET"])
def index():
    # отдадим содержимое static index.html
    # проще — прочитаем шаблон из файла index.html, но чтобы не зависеть от файловой структуры,
    # просто редиректим на статический файл.
    # Мы храним index.html в корне запуска (пользователь сохранит этот файл рядом).
    # Если запускаете Flask в dev, просто возвращаем содержимое:
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        # fallback: короткая страница
        return "<p>Поместите файл index.html в папку приложения и откройте /</p>"

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
            if not A:
                raise ValueError("Матрица A пуста")
            if not B:
                raise ValueError("Матрица B пуста (нужна для выбранной операции)")
            if op == "add":
                if shape(A) != shape(B):
                    raise ValueError("Для сложения размеры матриц должны совпадать")
                R = add(A,B)
                result_text = mat_to_text(R)
            elif op == "sub":
                if shape(A) != shape(B):
                    raise ValueError("Для вычитания размеры матриц должны совпадать")
                R = sub(A,B)
                result_text = mat_to_text(R)
            else: # mul
                R = mul(A,B)
                result_text = mat_to_text(R)
        else:
            if not A:
                raise ValueError("Матрица A пуста")
            if op == "transpose":
                R = transpose(A)
                result_text = mat_to_text(R)
            elif op == "det":
                d = det(A)
                # если близок к целому, покажем целое
                if abs(d - round(d)) < 1e-9:
                    d = round(d)
                result_text = str(d)
            elif op == "inverse":
                inv = inverse(A)
                result_text = mat_to_text(inv)
            else:
                raise ValueError("Неизвестная операция")
    except Exception as e:
        err = str(e)
    return render_template_string(RESULT_PAGE, op=op, err=err, result_text=result_text)

if __name__ == "__main__":
    # запускаем на localhost:5000
    app.run(debug=True)