import json
import os

DATA_FILE = "data/users.json"

def load_data():
    """Đọc toàn bộ dữ liệu người dùng từ users.json"""
    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    """Lưu dữ liệu người dùng vào users.json"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_user(user_id):
    """Lấy dữ liệu 1 user, nếu chưa có thì tạo mới"""
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "xu": 0,
            "love_partner": None,
            "intimacy": 0,
            "inventory": {},
            "materials": {},
            "luck": 0,
            "last_job": {},
            # Thêm các field mới cho hệ thống khung ảnh
            "owned_frames": ["frame_basic"],  # Khung mặc định
            "current_frame": "frame_basic",    # Khung đang dùng
            "married": False,                  # Trạng thái kết hôn
            "gifts_given": 0                   # Số quà đã tặng
        }
        save_data(data)
    else:
        # Đảm bảo các field mới tồn tại cho user cũ
        if "owned_frames" not in data[user_id]:
            data[user_id]["owned_frames"] = ["frame_basic"]
        if "current_frame" not in data[user_id]:
            data[user_id]["current_frame"] = "frame_basic"
        if "married" not in data[user_id]:
            data[user_id]["married"] = False
        if "gifts_given" not in data[user_id]:
            data[user_id]["gifts_given"] = 0
        save_data(data)
    
    return data[user_id]

def update_user(user_id, update_dict):
    """Cập nhật dữ liệu của 1 user"""
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        get_user(user_id)
    data[user_id].update(update_dict)
    save_data(data)
