# Датасет: https://www.kaggle.com/datasets/marvyaymanhalim/student-performance-and-attendance-dataset
import csv
import os
 
DATA_DIR = "data"
ATT_PATH = os.path.join(DATA_DIR, "attendance.csv")
OUT_DIR = "output"
 
 
# Алиса: утилиты чтения и нормализация статуса
def norm_status(s: str) -> str:
    if s is None:
        return ""
    t = str(s).strip().lower()
    if t in ("present", "p"):
        return "present"
    if t in ("absent", "a"):
        return "absent"
    if t in ("late", "l"):
        return "late"
    # если встретилось что-то странноe оставим как есть (но посчитаем отдельно)
    return t
 
 
def read_attendance_rows(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Не найдено: {path}. Проверь, что attendance.csv лежит в папке data/")
 
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            sid = (row.get("Student_ID") or "").strip()
            subject = (row.get("Subject") or "").strip()
            status = norm_status(row.get("Attendance_Status"))
 
            # минимальная проверка (чтобы не ломалось)
            if not sid or not subject or not status:
                continue
 
            rows.append({"student_id": sid, "subject": subject, "status": status})
 
    if not rows:
        raise ValueError("Не получилось прочитать строки. Проверь названия колонок: Student_ID, Subject, Attendance_Status")
 
    return rows
 
 
# Софа: статистика по предметам
def stats_by_subject(rows):
    # subject -> counters
    d = {}
    for r in rows:
        subj = r["subject"]
        st = r["status"]
 
        c = d.setdefault(subj, {"subject": subj, "total": 0, "present": 0, "late": 0, "absent": 0, "other": 0})
        c["total"] += 1
 
        if st == "present":
            c["present"] += 1
        elif st == "late":
            c["late"] += 1
        elif st == "absent":
            c["absent"] += 1
        else:
            c["other"] += 1
 
    out = []
    for subj, c in d.items():
        total = c["total"]
        # считаем посещаемость как (present + late) / total
        c["attendance_rate"] = (c["present"] + c["late"]) / total if total else 0.0
        out.append(c)
 
    out.sort(key=lambda x: x["attendance_rate"], reverse=True)
    return out
 
 
# Красная: статистика по студенту и предмету
def stats_by_student_subject(rows):
    # (student_id, subject) -> counters
    d = {}
    for r in rows:
        key = (r["student_id"], r["subject"])
        st = r["status"]
 
        c = d.setdefault(
            key,
            {
                "student_id": r["student_id"],
                "subject": r["subject"],
                "total": 0,
                "present": 0,
                "late": 0,
                "absent": 0,
                "other": 0,
            },
        )
        c["total"] += 1
 
        if st == "present":
            c["present"] += 1
        elif st == "late":
            c["late"] += 1
        elif st == "absent":
            c["absent"] += 1
        else:
            c["other"] += 1
 
    out = []
    for _, c in d.items():
        total = c["total"]
        c["attendance_rate"] = (c["present"] + c["late"]) / total if total else 0.0
        out.append(c)
 
    # сортировка: сначала предмет, потом по посещаемости
    out.sort(key=lambda x: (x["subject"], x["attendance_rate"]), reverse=True)
    return out
 
 
# Кейпоп:s сохранение файлов
def write_csv(path, rows, fieldnames):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
 
 
def write_report(path, total_rows, subject_rows):
    lines = []
    lines.append("ОТЧЕТ: посещаемость занятий по предметам")
    lines.append("")
    lines.append(f"Обработано записей посещаемости: {total_rows}")
    lines.append("")
    lines.append("Наиболее посещаемые:")
    for s in subject_rows[:3]:
        lines.append(f"  - {s['subject']}: attendance_rate={s['attendance_rate']:.3f}, total={s['total']}")
    lines.append("")
    lines.append("Наименее посещяемые:")
    for s in list(reversed(subject_rows[-3:])):
        lines.append(f"  - {s['subject']}: attendance_rate={s['attendance_rate']:.3f}, total={s['total']}")
 
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
 
 
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
 
    rows = read_attendance_rows(ATT_PATH)
 
    subj_rows = stats_by_subject(rows)
    ss_rows = stats_by_student_subject(rows)
 
    # сохраняем минимум полезных итогов
    write_csv(
        os.path.join(OUT_DIR, "attendance_by_subject.csv"),
        subj_rows,
        ["subject", "total", "present", "late", "absent", "other", "attendance_rate"],
    )
    write_csv(
        os.path.join(OUT_DIR, "attendance_by_student_subject.csv"),
        ss_rows,
        ["student_id", "subject", "total", "present", "late", "absent", "other", "attendance_rate"],
    )
    write_report(os.path.join(OUT_DIR, "report.txt"), total_rows=len(rows), subject_rows=subj_rows)
 
    print("готово")
    print("файлы в output/:")
    print(" - attendance_by_subject.csv")
    print(" - attendance_by_student_subject.csv")
    print(" - report.txt")
 
 
if __name__ == "__main__":
    main()