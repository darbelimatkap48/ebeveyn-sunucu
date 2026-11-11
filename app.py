from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tasks_db = {}

@app.route('/')
def index():
    return "Ebeveyn Kontrol API Sunucusu Aktif!"

@app.route('/api/tasks/<device_id>', methods=['GET'])
def get_tasks(device_id):
    device_tasks = tasks_db.get(device_id, [])
    pending_tasks = [t for t in device_tasks if t.get('status') == 'pending']
    return jsonify(pending_tasks)

@app.route('/api/tasks/update', methods=['POST'])
def update_task():
    data = request.json
    task_id = data.get('task_id')
    status = data.get('status')
    for device, tasks in tasks_db.items():
        for task in tasks:
            if task.get('task_id') == str(task_id):
                task['status'] = status
                return jsonify({"message": "Görev güncellendi", "success": True})
    return jsonify({"message": "Görev bulunamadı", "success": False}), 404

@app.route('/api/upload/<device_id>', methods=['POST'])
def upload_file(device_id):
    if 'file' not in request.files:
        return jsonify({"error": "Dosya bulunamadı"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Dosya seçilmemiş"}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{device_id}_{filename}")
    file.save(save_path)
    return jsonify({"message": f"{filename} başarıyla alındı", "success": True})

@app.route('/api/add_task', methods=['POST'])
def add_task():
    data = request.json
    device_id = data.get('device_id')
    if not device_id:
        return jsonify({"error": "device_id gerekli"}), 400
    if device_id not in tasks_db:
        tasks_db[device_id] = []
    new_task = {
        "task_id": str(len(tasks_db[device_id]) + 1),
        "action": data.get('action'),
        "file_path": data.get('file_path'),
        "status": "pending"
    }
    tasks_db[device_id].append(new_task)
    return jsonify({"message": "Görev sıraya alındı", "task": new_task})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
