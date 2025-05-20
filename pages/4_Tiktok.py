import streamlit as st
from database_utils import get_distinct_user_ids_from_db, get_info_by_user_id, delete_user_by_id
import pandas as pd
from send_request import send_request, stop_dag
import os
import time
import re

def show_user_info(user_id):
    user_detail = get_info_by_user_id(user_id, platform='tiktok')
    st.markdown("---")
    # Nếu là object, chuyển sang dict
    infos = pd.DataFrame(columns=["video_id", "transcript"])
    for item in user_detail:
        display_info = {
            "video_id": item.video_id,
            "transcript": item.transcript}
        infos = pd.concat([infos, pd.DataFrame([display_info])], ignore_index=True)
        # st.write(item.__dict__['transcript'])
    st.markdown(infos.to_html(escape=False), unsafe_allow_html=True)

@st.dialog("Xóa người dùng TikTok", width="large")
def delete_user(user_id):
    st.write("Xóa người dùng TikTok khỏi cơ sở dữ liệu")
    if user_id:
        st.write(f"Bạn có chắc chắn muốn xóa người dùng {user_id} không?")
        if st.button("Xóa"):
            delete_user_by_id(user_id, platform='tiktok')
            st.success(f"Đã xóa người dùng {user_id} khỏi cơ sở dữ liệu.")
            st.rerun()
    else:
        st.warning("Không có người dùng nào được chọn.")        

def display_tiktok_users():
    # status_placeholder = st.empty()
    # Get distinct user IDs from the database
    user_ids = get_distinct_user_ids_from_db(platform='tiktok')
    users = pd.DataFrame(columns=["STT", "user_id", "link"])
    if user_ids:
        for idx, user_id in enumerate(user_ids, start=1):
            # Nếu user_id là tuple, lấy phần tử đầu tiên
            user_id = user_id[0]
            user_id = str(user_id)  # Đảm bảo user_id là chuỗi
            user_link = f"[https://www.tiktok.com/@{user_id}](https://www.tiktok.com/@{user_id})"
            # Thêm dòng mới vào DataFrame
            users = pd.concat([
                users,
                pd.DataFrame([{"STT": idx, "user_id": user_id, "link": user_link}])
            ], ignore_index=True)

        # Hiển thị tiêu đề cột
        header = st.columns([1, 3, 5, 2])
        header[0].write("STT")
        header[1].write("User ID")
        header[2].write("Link")
        header[3].write("Xóa")

        @st.dialog(f"Chi tiết người dùng: {user_id}", width="large")
        def show_user_info_dialog(user_id):
            show_user_info(user_id)

        # Hiển thị bảng với nút cho mỗi hàng
        for index, row in users.iterrows():
            cols = st.columns([1, 3, 5, 2])  # 4 cột: STT, user_id, link, nút Xóa
            cols[0].write(row["STT"])
            # Nút bấm vào user_id để xem chi tiết
            if cols[1].button(row["user_id"], key=f"user_{index}"):
                st.session_state["selected_user_id"] = row["user_id"]
                show_user_info_dialog(row["user_id"])
            cols[2].markdown(row["link"], unsafe_allow_html=True)
            if cols[3].button("Xóa", key=f"btn_{index}"):
                delete_user(row["user_id"])
                # st.rerun()

    else:
        st.write("Không có người dùng nào trong cơ sở dữ liệu.")
    

@st.dialog("Thêm người dùng TikTok", width="large")
def add_tiktok_user():
    st.write("Thêm người dùng TikTok vào cơ sở dữ liệu")
    user_id = st.text_input("Nhập user_id TikTok", placeholder="Nhập user_id TikTok")
    if st.button("Thêm"):
        if user_id:
            # Gửi yêu cầu đến API
            with st.spinner('Đang gửi yêu cầu tới Airflow...'):
                success, message, dag_run_id = send_request(id=user_id, count=5, platform="tiktok")
                if success:
                    st.success(message)
                    st.session_state['dag_run_id'] = dag_run_id  # Lưu lại để tiếp tục theo dõi log
                else:
                    st.error(message)
        else:
            st.warning("Vui lòng nhập user_id TikTok.")

    def get_task_status_from_log(log_file_path):
        if not os.path.exists(log_file_path):
            return "", "", "chưa chạy"  # Trả về 3 giá trị
        with open(log_file_path, "r") as f:
            content = f.read()
            if "Done" in content and "Error" not in content:
                match = re.search(r"Downloaded\s+(\d+)\s+new videos", content)
                if match:
                    new_videos = match.group(1)
                    downloaded = int(content.count("Downloaded successfully"))
                else:
                    match = re.search(r"Number of downloads to process:\s*(\d+)", content)
                    if match:
                        new_videos = match.group(1)
                        downloaded = content.count("Processing audio with duration")
                    else:
                        new_videos = 0
                        downloaded = 0
                
                return new_videos, downloaded, "thành công"
            elif "Task is not able to be run" in content or "Error" in content:
                return "", "", "thất bại"
            elif "Downloading" in content or "Processing" in content:
                match = re.search(r"New videos:\s*(\d+)", content)
                if match:
                    new_videos = match.group(1)
                    downloaded = content.count("Downloaded successfully")
                else:
                    match = re.search(r"Number of downloads to process:\s*(\d+)", content)
                    new_videos = match.group(1)
                    downloaded = content.count("Processing audio with duration")
                return new_videos, downloaded, "đang chạy"
            else:
                return "", "", "chưa chạy"            

    # Nếu đã có dag_run_id, tiếp tục hiển thị trạng thái DAG và Task
    dag_id = "tiktok_videos_scraper_dag"
    dag_run_id = st.session_state.get('dag_run_id', None)
    if dag_run_id is None:
        st.warning("Chưa có DAG nào được chạy. Vui lòng gửi yêu cầu trước.")
        st.stop()
    # dag_run_id = "manual__2025-05-16T08:47:54.480844+00:00"
    task_id = "tiktok_videos_scraper_task"
    task_status_list = [    
        {"Task": "Download", "Trạng thái": "chưa chạy"},
        {"Task": "Chuyển đổi video thành transcript", "Trạng thái": "chưa chạy"}
    ]

    if 'dag_run_id' in st.session_state:
        dag_run_id = st.session_state['dag_run_id']
    st.title("Theo dõi trạng thái DAG và Task")

    status_placeholder = st.empty()  # Tạo placeholder cho bảng trạng thái

    # Hàm cập nhật trạng thái task
    def get_status_list():
        download_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=tiktok_videos_scraper_task/attempt=1.log"
        transcript_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=audio_to_transcript_task/attempt=1.log"
        new_videos, downloaded_videos, download_task_state = get_task_status_from_log(download_log_file_path)
        new_transcripts, transcripted, transcript_task_state = get_task_status_from_log(transcript_log_file_path)
        return [{"Task": "Download", "Trạng thái": download_task_state, "Số video mới": new_videos, "Số video đã tải về": downloaded_videos}, 
                {"Task": "Chuyển đổi video thành transcript", "Trạng thái": transcript_task_state, "Số video mới": new_transcripts, "Số video đã chuyển đổi": transcripted}]
        
    def check_task_status():
        if task_status_list[0]["Trạng thái"] == "thành công" and task_status_list[1]["Trạng thái"] == "thành công":
            return True
        return False
   
    start_time = time.time()
    timeout = 60  # 2 phút

    while not check_task_status():
        task_status_list = get_status_list()
        status_placeholder.table(task_status_list)

        # Kiểm tra nếu task đầu tiên vẫn "chưa chạy" sau 2 phút
        if task_status_list[0]["Trạng thái"] == "chưa chạy":
            elapsed = time.time() - start_time
            if elapsed > timeout:
                stop_dag_result, stop_dag_message = stop_dag(dag_id, dag_run_id)
                if stop_dag_result:
                    st.success(stop_dag_message)
                else:
                    st.error(stop_dag_message)
                st.error("Task chưa chạy sau 1 phút. Đã gửi yêu cầu dừng DAG.")
                break
        else:
            start_time = time.time()  # Reset nếu trạng thái thay đổi
    
        time.sleep(1)  # Thêm sleep để tránh vòng lặp quá nhanh

    task_status_list = get_status_list()
    status_placeholder.table(task_status_list)
    if check_task_status():
        st.success("DAG đã hoàn thành!")
        # Thông báo số lượng video đã tải về
        # ???
        del st.session_state['dag_run_id']
        show_user_info(user_id)

    if st.button("Close"):
        st.rerun()

st.title('Danh sách người dùng TikTok')    
display_tiktok_users()
if st.button("Thêm người dùng TikTok"):
    add_tiktok_user()