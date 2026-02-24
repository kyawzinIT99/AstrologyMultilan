import modal

app = modal.App.lookup("astrology-chatbot-mm")
volume = modal.Volume.from_name("astrology-bookings-vol")

@app.function(volumes={"/data": volume})
def check_reports():
    import os
    report_dir = "/data/reports"
    if not os.path.exists(report_dir):
        return f"Directory {report_dir} does not exist"
    
    files = os.listdir(report_dir)
    result = []
    for f in files:
        path = os.path.join(report_dir, f)
        size = os.path.getsize(path)
        result.append(f"{f}: {size} bytes")
    return "\n".join(result)

with app.run():
    print(check_reports.remote())
