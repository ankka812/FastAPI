from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi import FastAPI
from typing import Optional

app = FastAPI()

tasks =[]
pomodoro_sessions = []

@app.post("/tasks")
def create_task(title: str, description: Optional[str] = None, status: str = "to do"):
    task_id = len(tasks) + 1
    if len(title) < 3 or len(title) > 100:
        raise HTTPException(status_code=400, detail="Title must be between 1 and 100 characters")
    if description and len(description) > 300:
        raise HTTPException(status_code=400, detail="Description can have a max of 300 characters")
    if status not in ["to do", "in progress", "done"]:
        raise HTTPException(status_code=400, detail="Status must be one of these options: to do, in progress or done")
    for task in tasks:
        if task["title"] == title:
            raise HTTPException(status_code=400, detail="Title must be unique")
    tasks.append({"id": task_id, "title": title, "description": description, "status": status})

@app.get("/tasks")
def get_tasks(status: Optional[str] = None):
    if status:
        return [task for task in tasks if task["status"] == status]
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task['id'] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Id does not exist")

@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str, description: Optional[str] = None, status: str = "to do"):
    for task in tasks:
        if task['id'] == task_id:
            if title:
                if len(title) < 3 or len(title) > 100:
                    raise HTTPException(status_code=400, detail="Title must be between 1 and 100 characters")
                if any(t["title"] == title for t in tasks if t["id"] != task_id):
                    raise HTTPException(status_code=400, detail="Title must be unique")
                task["title"] = title
            if description:
                if len(description) > 300:
                    raise HTTPException(status_code=400, detail="Description can have a max of 300 characters")
                task["description"] = description
            if status:
                if status not in ["to do", "in progress", "done"]:
                    raise HTTPException(status_code=400, detail="Status must be one of these options: to do, in progress or done")
                task["status"] = status
            return {"message": "Task updated"}
    raise HTTPException(status_code=404, detail="Id does not exist")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in tasks:
        if task['id'] == task_id:
            tasks.remove(task)
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Id does not exist")

@app.post("/pomodoro")
def create_pomodoro(task_id: int):
    task_exists = False
    for task in tasks:
        if task['id'] == task_id:
            task_exists = True
            break

    if not task_exists:
        raise HTTPException(status_code=400, detail="Id does not exist")

    for pomodoro_session in pomodoro_sessions:
        if pomodoro_session['id'] == task_id and not pomodoro_session['completed']:
            raise HTTPException(status_code=400, detail="Previous pomodoro session is not completed")

    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=25)
    pomodoro_sessions.append({"id": task_id, "start_time": start_time, "end_time": end_time, "completed": False})

    return {"message": "Pomodoro session created"}

@app.post("/pomodoro/{task_id}/stop")
def stop_pomodoro(task_id: int):
    for pomodoro_session in pomodoro_sessions:
        if pomodoro_session['id'] == task_id:
            if not pomodoro_session["completed"]:
                pomodoro_session["completed"] = True
                pomodoro_session["end_time"] = datetime.utcnow()
                return {"message": "Pomodoro session stopped"}
            raise HTTPException(status_code=400, detail="Pomodoro session already completed")
    raise HTTPException(status_code=400, detail="Id not found")

@app.get("/pomodoro/stats")
def get_pomodoro_stats():
    stats = {}
    for pomodoro_session in pomodoro_sessions:
        if pomodoro_session["completed"] is True:
            duration = (pomodoro_session["end_time"] - pomodoro_session["start_time"]).seconds // 60
            task_id = pomodoro_session["id"]
            if task_id not in stats:
                stats[task_id] = {"completed_sessions": 0, "total_time": 0}
            stats[task_id]["completed_sessions"] += 1
            stats[task_id]["total_time"] += duration

    return stats



