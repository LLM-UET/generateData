import os
import csv
from openai import OpenAI

# Lấy API key từ biến môi trường
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("ERROR: Chưa đặt biến môi trường OPENAI_API_KEY!")

client = OpenAI(api_key=api_key)

INPUT_FILE = "tiktok_comments.csv"
OUTPUT_FILE = "tiktok_comments_labeled.csv"


def classify_comment(text: str) -> str:
    prompt = f"""
    Phân loại cảm xúc bình luận tiếng Việt sau thành 1 trong 3 nhãn:
    - Positive
    - Neutral
    - Negative

    Chỉ trả về duy nhất một từ trong ba nhãn trên.

    Bình luận: "{text}"
    """

    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # model rẻ
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    # Bản mới dùng .content, không dùng ["content"]
    label = resp.choices[0].message.content.strip()
    return label


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f_in, \
         open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f_out:

        reader = csv.reader(f_in)
        writer = csv.writer(f_out, quotechar='"', quoting=csv.QUOTE_ALL)

        # Đọc dòng đầu tiên, xem có phải header không
        first_row = next(reader)
        writer.writerow(["comment", "label"])

        # Nếu dòng đầu không phải header thì xử lý luôn
        start_index = 2
        if first_row and first_row[0].strip().lower() != "comment":
            comment = first_row[0].strip()
            if comment:
                label = classify_comment(comment)
                writer.writerow([comment, label])
                print(f"[1] {comment} → {label}")
        else:
            start_index = 2

        # Xử lý các dòng còn lại
        for idx, row in enumerate(reader, start=start_index):
            if not row:
                continue
            comment = row[0].strip()
            if not comment:
                continue

            label = classify_comment(comment)
            writer.writerow([comment, label])
            print(f"[{idx}] {comment} → {label}")

    print("\nHoàn tất. Kết quả lưu vào:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
