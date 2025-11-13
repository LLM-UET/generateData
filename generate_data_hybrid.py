import os
import argparse
from openai import OpenAI

# ============================================================
# PROMPT: Sinh dữ liệu cảm xúc hội thoại Viettel
# ============================================================
PROMPT_BASE = """
Hãy tạo bộ dữ liệu gồm các cặp (text, label) để huấn luyện mô hình phân loại cảm xúc trong các đoạn hội thoại giữa khách hàng và chatbot chăm sóc khách hàng của Viettel.

Quy định dữ liệu:
- Mỗi dòng là một tin nhắn do người dùng (user) gửi trong hội thoại với chatbot, KHÔNG bao gồm tin nhắn phản hồi của AI.
- Ngôn ngữ: tiếng Việt tự nhiên, theo phong cách hội thoại chat thực tế (Zalo, app Viettel, hoặc web chat).
- Chủ đề hội thoại: chỉ xoay quanh các vấn đề liên quan đến **các gói mạng Viettel**, **SIM**, **data 4G**, **tốc độ mạng**, **đăng ký/hủy/gia hạn gói cước**, **lỗi mạng**, **trừ tiền oan**, **không có sóng**, **mạng yếu**, **nạp tiền**, v.v.
- Các gói mạng tham khảo: V90B, ST70K, MXH100, SD70, F90, Umax, Mimax70.
- Một số câu có thể nhắc trực tiếp tên gói, hoặc chỉ nói chung (ví dụ: “mạng yếu quá”, “đăng ký hoài không được”).
- Mỗi câu là **một lượt hội thoại độc lập**, không cần mạch nối giữa các dòng.
- Một số câu có thể là phản ứng ngắn với AI như:
  - "Ủa sao kỳ vậy"
  - "Anh làm đúng cú pháp rồi mà"
  - "Cảm ơn bot nha"
  - "Gửi giúp anh tin nhắn đăng ký luôn được không"

Phong cách ngôn ngữ:
- Câu ngắn dài linh hoạt: có thể chỉ 1–2 từ (“Bực ghê”, “Ngon nè”) hoặc dài đến 20–25 từ (“Anh đăng ký gói ST70K rồi mà vẫn không có data, sao lạ vậy trời”).
- Có thể **không có dấu câu**, **viết tắt**, hoặc **không viết hoa đầu câu** để giống hội thoại thật.
- Có thể chứa emoji hoặc ký hiệu kiểu chat (“haizz”, “:)))”, “^^”, “...”).
- Giữ phong cách tự nhiên, thân mật.

Nhãn cảm xúc:
Gồm 3 loại:
- Neutral (0): Bình thường / trung tính. Ví dụ: “Đăng ký gói V90B thế nào vậy?”, “Cú pháp hủy gói ST70K là gì?”
- Negative (1): Tiêu cực / bực bội. Ví dụ: “Mạng yếu quá trời luôn”, “Bực! Không hủy được gói!”
- Positive (2): Tích cực / hài lòng. Ví dụ: “Đăng ký gói ST70K ngon lành luôn!”, “Cảm ơn nhé!”

Tỉ lệ:
- 40% Neutral
- 40% Negative
- 20% Positive

Thông tin gói mạng để tham khảo:
- **V90B**: 90k/tháng. Miễn phí 60GB data (2GB/ngày) + 1000 phút nội mạng.
- **ST70K**: 70k/tháng. 30GB data (1GB/ngày).
- **MXH100**: 100k/tháng. Truy cập không giới hạn Facebook, TikTok, YouTube.
- **SD70**: 70k/tháng. 3GB data + gọi nội mạng miễn phí dưới 10 phút.
- **F90**: 90k/tháng. 7GB data + 500 phút nội mạng.
- **Umax**: 120k/tháng. Data không giới hạn (giảm tốc sau 5GB/ngày).
- **Mimax70**: 70k/tháng. 3GB/tháng, hết dung lượng giảm tốc độ.

Quy mô:
Tạo {n_lines} dòng dữ liệu.

Yêu cầu định dạng output:
- Output dạng CSV, **không có header**.
- Mỗi dòng có hai cột:
  1. text (bọc trong dấu nháy kép)
  2. label (Positive, Negative, hoặc Neutral)
Ví dụ:
"Giá đắt quá, có cái nào rẻ hơn không?",Negative
"Gói này được quá nhỉ",Positive
"Cái này cũng tạm được",Neutral
"""

# ============================================================
# HÀM HỖ TRỢ
# ============================================================
def ensure_utf8_bom(path: str):
    """Tạo BOM ở đầu file để Excel hiển thị tiếng Việt đúng"""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "wb") as fb:
            fb.write(b"\xef\xbb\xbf")

def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("❌ Thiếu OPENAI_API_KEY. Hãy set biến môi trường trước khi chạy.")
    return OpenAI(api_key=api_key)

def call_api(client, model, n_lines, temperature=0.8):
    prompt = PROMPT_BASE.format(n_lines=n_lines)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Bạn là chuyên gia xử lý ngôn ngữ, tạo dữ liệu hội thoại tiếng Việt."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

# ============================================================
# CHẠY SINH DỮ LIỆU (HYBRID)
# ============================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outfile", type=str, default="data.csv")
    parser.add_argument("--total", type=int, default=1000)
    parser.add_argument("--chunk", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=0.8)
    args = parser.parse_args()

    client = get_client()
    ensure_utf8_bom(args.outfile)

    total, chunk = args.total, args.chunk
    written = 0

    with open(args.outfile, "a", encoding="utf-8", newline="") as f:
        while written < total:
            # 100 dòng đầu -> GPT-4o (chất lượng cao)
            if written < 100:
                model = "gpt-4o"
            else:
                model = "gpt-4o-mini"

            need = min(chunk, total - written)
            print(f"🟢 Generating {need} lines with model: {model}")
            data = call_api(client, model, need, args.temperature)

            # ------------------------------
            # 🧹 Lọc các dòng hợp lệ thật sự
            # ------------------------------
            clean_lines = []
            for ln in data.splitlines():
                ln = ln.strip()
                # Giữ lại dòng hợp lệ kiểu "..." ,Positive/Negative/Neutral
                if ln.startswith('"') and (",Positive" in ln or ",Negative" in ln or ",Neutral" in ln):
                    clean_lines.append(ln)

            for ln in clean_lines:
                f.write(ln + "\n")

            print(f"✅ Đã ghi {len(clean_lines)} dòng (đã lọc rác).")
            written += len(clean_lines)

    print(f"\n🎯 Hoàn tất. File '{args.outfile}' hiện có thêm {written} dòng dữ liệu cảm xúc hội thoại.")

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    main()
