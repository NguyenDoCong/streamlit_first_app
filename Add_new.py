import streamlit as st
import pandas as pd
from send_request import send_request
from database_utils import get_all_videos_from_db
import time
import os
import requests

# def get_dag_status(dag_id, dag_run_id):
#     url = f"http://localhost:8080/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
#     response = requests.get(url, auth=("airflow", "airflow"))
#     if response.status_code == 200:
#         return response.json().get("state", "running")
#     return "running"

# def get_task_status(dag_id, dag_run_id, task_id):
#     url = f"http://localhost:8080/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances/{task_id}"
#     response = requests.get(url, auth=("airflow", "airflow"))
#     if response.status_code == 200:
#         return response.json().get("state", "running")
#     return "running"

def get_task_status_from_log(log_file_path):
    if not os.path.exists(log_file_path):
        return "chưa chạy"
    with open(log_file_path, "r") as f:
        content = f.read()
        # return content
        # st.write(content)
    
        if "Done" in content or "Task exited with return code 0" in content:
            return "thành công"
        elif "Marking task as FAILED" in content or "Error" in content:
            return "thất bại"
        elif "Downloading" in content or "Processing" in content:
            return "đang chạy"
        else:
            return "chưa chạy"

st.title('Phân tích video từ mạng xã hội')

option = st.selectbox(
    "Chọn mạng xã hội?",
    ("facebook", "instagram", "x", "tiktok"),
)
def reset_id():
    st.session_state.id = ''
    
with st.form('my_form'):
    
    id = st.text_input('Điền id', value=st.session_state.get('id', ''), key='id')
    count = st.text_input('Số kết quả tối thiểu', value=st.session_state.get('count', ''), key='count')
  
    if count:
        count = int(count)
    else:
        count = 0
    # st.write('Value:', id)
    submit = st.form_submit_button(label='Gửi yêu cầu')

if submit:
    with st.spinner('Đang gửi yêu cầu tới Airflow...'):
        success, message, dag_run_id = send_request(id=id, count=count, platform=option)
        if success:
            st.success(message)
            st.session_state['dag_run_id'] = dag_run_id  # Lưu lại để tiếp tục theo dõi log
        else:
            st.error(message)

st.write("Mạng xã hội:", option)

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
dag_id = f"{option}_videos_scraper_dag"
st.title("Theo dõi trạng thái DAG và Task")

status_placeholder = st.empty()  # Tạo placeholder cho bảng trạng thái

# Hàm cập nhật trạng thái task
def get_status_list():
    download_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=tiktok_videos_scraper_task/attempt=1.log"
    transcript_log_file_path = f"/home/docon/projects/airflow-docker/logs/dag_id={dag_id}/run_id={dag_run_id}/task_id=audio_to_transcript_task/attempt=1.log"
    download_task_state = get_task_status_from_log(download_log_file_path)
    transcript_task_state = get_task_status_from_log(transcript_log_file_path)
    return [
        {"Task": "Download", "Trạng thái": download_task_state},
        {"Task": "Chuyển đổi video thành transcript", "Trạng thái": transcript_task_state}
    ]

def check_task_status():
    if task_status_list[0]["Trạng thái"] == "thành công" and task_status_list[1]["Trạng thái"] == "thành công":
        return True
    return False

check_task_status = check_task_status()
while not check_task_status:
    task_status_list = get_status_list()
    status_placeholder.table(task_status_list)
    if task_status_list[0]["Trạng thái"] == "thành công" and task_status_list[1]["Trạng thái"] == "thành công":
        st.success("DAG đã hoàn thành!")
        del st.session_state['dag_run_id']
        df = get_all_videos_from_db(platform=option)
        break
    # elif task_status_list[0]["Trạng thái"] == "thất bại" or task_status_list[1]["Trạng thái"] == "thất bại":
    #     st.error("DAG đã thất bại!")
    #     break
    # elif task_status_list[0]["Trạng thái"] == "chưa chạy" and task_status_list[1]["Trạng thái"] == "chưa chạy":
    #     st.warning("DAG vẫn đang chạy!")

task_status_list = get_status_list()
status_placeholder.table(task_status_list)
df= get_all_videos_from_db(platform=option)

# if df is None:
#     st.error("No data returned from database!")
# elif len(df) == 0:
#     st.warning("No records found for platform 'tiktok'.")
# else:
#     # Convert list of ORM objects to DataFrame
#     df = pd.DataFrame([row.__dict__ for row in df])
#     # Remove SQLAlchemy internal state column if present
#     if '_sa_instance_state' in df.columns:
#         df = df.drop('_sa_instance_state', axis=1)
#     # st.write("Shape of df:", df.shape)
#     # st.write(df.head())
#     columns_to_show = ['video_id', 'transcript', 'status']
#     df = df[columns_to_show]
#     st.dataframe(df)