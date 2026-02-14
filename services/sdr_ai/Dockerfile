FROM python:3.11-slim
WORKDIR /srv
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY services/sdr_ai/app.py ./service.py
COPY services/sdr_ai/models/rf_signature_model.json /models/rf_signature_model.json
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8100"]
