FROM node:22-alpine AS frontend-builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend_api.py ./
COPY --from=frontend-builder /app/dist ./dist
EXPOSE 8100
CMD ["uvicorn", "backend_api:app", "--host", "0.0.0.0", "--port", "8100"]
