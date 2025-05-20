import requests
from requests.auth import HTTPBasicAuth

def send_request(id="hoaminzy_hoadambut",count=20, platform="tiktok"):
    """
    Function to send a request to the Airflow API to trigger a DAG run.
    """
    # URL for the Airflow API endpoint
    # Replace with your Airflow instance URL if not running locally
    # Example: url = "http://your-airflow-instance:8080/api/v1/dags/tiktok_videos_scraper_dag/dagRuns"
    url = f"http://localhost:8080/api/v1/dags/{platform}_videos_scraper_dag/dagRuns"
    payload = {
        "conf": {
            "id": id,
            "count": count
        }
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url,
            json=payload,
            auth=HTTPBasicAuth("airflow", "airflow"),
            headers=headers,
            timeout=10
        )
        if response.status_code == 200 or response.status_code == 201:
            return True, f"Đã gửi yêu cầu thành công với ID: {id} và số lượng: {count}.", response.json()['dag_run_id']
        else:
            return False, f"Lỗi: {response.status_code} - {response.text}", ""
    except Exception as e:
        return False, f"Lỗi kết nối: {str(e)}", ""
    
def stop_dag(dag_id, dag_run_id):
    airflow_url = "http://localhost:8080"
    endpoint = f"/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"
    url = airflow_url + endpoint

    payload = {"state": "failed"}  # hoặc "success" nếu muốn kết thúc thành công
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.patch(
            url,
            json=payload,
            auth=HTTPBasicAuth("airflow", "airflow"),
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            return True, f"Đã gửi yêu cầu dừng DAG {dag_id} với run_id {dag_run_id}"
        else:
            return False, f"Lỗi khi dừng DAG: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Lỗi khi gửi request dừng DAG: {e}"
    
#main method
if __name__ == "__main__":
    send_request()