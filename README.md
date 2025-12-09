# Reverse Image Search

Product Search with DINOv2 and FAISS:
This is end-to-end reverse image search engine where user upload a image and can retrieve similar items. Pre-trained transformer backbone (DINOv2 Vision) was fine-tuned with a custom 128-D projection head via triplet loss with semi-hard negative mining on ~25k images. The web application combines a lightweight web client, a FastAPI inference service, and FAISS-based vector search over fine tuned DINOv2 embeddings, and is deployed on AWS using ECS, FARGATE.

The fine-tuned model achieves:
- **~85.6% Recall@1**
- **~94.42% Recall@5**
- **~96.5% Recall@10**

## Business problem:
In the fast-paced landscape of fashion, the increasing volume of visual content poses a challenge for efficient search and retrieval. Recognizing this, this project aims to introduce a solution – the Deep Learning Based reverse image search. This project involves utilizing Deep Learning to analyze the intricate patterns within the user-shared image, enabling the identification of the outfit they wish to find, and suggest similar items.

## Demo:


## System Architecture
The system has two main parts:
1. Offline training & bundling: Fine-tuned DINOv2 + projection head and build the FAISS index.
2. Online inference & search: serve the trained model behind a browser UI.

## Offline Model training & bundling 

![Offline training architecture](Images/Offline_training.png)

- Detail process: 
  - Loaded the Pre-trained DINOv2 backbone.
  - Fine tuned it with a 128-D projection head using triplet loss + semi-hard mining on ~25k fashion images.
  - Computed embeddings for every gallery image.
  - Built a FAISS index and metadata mapping id 
  - Calculated the recall as Recall@1: 85.56%, Recall@5: 94.42%, Recall@10: 96.46%

Model was trained on Google Colab using Nvidia A100 GPU. 
Outputs of Offline training: 
- model weights + config,
- FAISS index + metadata


## Online inference & search

![Online search architecture](Images/Online_Search_Architecture.png)

- Browser uploads query image via `/api/search-image`, served by the Node/Express frontend (ECS Fargate) behind ALB.
- FastAPI service (ECS Fargate) encodes the query with DINOv2, searches the in-memory FAISS index, and returns JSON results with `/api/thumb` URLs.
- For each image/thumbnail request, FastAPI pulls from the in-memory LRU cache when available; on a cache miss it downloads the gallery asset from S3 (or Hugging Face, depending on config) and streams the JPEG bytes back to the client.
- Model weights, FAISS index, and gallery metadata are downloaded during startup from S3 so the inference container is self-contained.


## Model & Dataset details
This project uses the **In-Shop Clothes Retrieval** dataset, which is organized into three logical parts:

- **train** – images used to learn the embedding model
- **query** – query images used only at evaluation time
- **gallery** – catalog images retrieved at evaluation time

### Train / Validation Split

To monitor overfitting and tune hyperparameters, the training data is split into **train** and **validation** subsets. Model wtraining is performed on the `train` partition only.

1. Load the `train` split as an `InShopDataset`.
2. Shuffle all indices.
3. Reserve a fixed fraction (`VAL_SPLIT_RATIO`, e.g. 10%) as the **validation set**.
4. Use the remaining images as the **training set**.

This gives two disjoint loaders:

- `train_loader` – used to optimize the DINOv2 + 128-D embedding head with triplet loss.
- `val_loader` – used to track validation loss/recall during training.

### Test / Retrieval Evaluation

Final retrieval performance is measured on the **standard In-Shop protocol**:

1. Build an `InShopEvalDataset` for the **gallery** split and compute embeddings for all gallery images with the trained model.
2. Build another `InShopEvalDataset` for the **query** split and compute embeddings for all query images.
3. For each query embedding, perform vector search over the gallery embeddings using **FAISS**.
4. Compute **Recall@K** metrics:
   - **Recall@1** – how often the correct item is the top result.
   - **Recall@5** – how often the correct item appears in the top 5 results.
   - **Recall@10** – how often the correct item appears in the top 10 results.

In this project, the trained model achieves approximately:

- **~85.6% Recall@1**
- **~94.42% Recall@5**
- **~96.5% Recall@10**


### Frontend (public/)
-  HTML/CSS/JS 
- `public/app.js` handles validation, previews, multipart uploads, streaming thumbnails, and UX states.
- The Express wrapper (server.js) serves the bundle and proxies /api/* for deployment

### Backend API (backend/)
- `backend/main.py` bootstraps FastAPI, wires routers, and injects singleton instances of the embedding model + FAISS index.
- Routes:
  - `/api/search-image` – accepts multipart uploads, encodes via DINOv2, and queries FAISS for top-K matches.
  - `/api/thumb/{idx}` – streams JPEG thumbnails; uses Hugging Face or S3 with LRU caching in `models/lazy_loader.py`.
  - `/api/health` – exposes device info, corpus size, and storage mode for monitoring.
- CORS, static hosting, and thumbnail sizing derive from environment variables defined in `config.env`.

### Machine Learning + Retrieval Layer
- **EmbeddingModel** (`backend/models/embedding.py`) loads the architecture/weights specified in `bundle/model/` (JSON + PT).
- Embeddings are normalized vectors (default 128-dim) generated by a configurable DINOv2 backbone.
- **FAISSIndex** (`backend/models/faiss_index.py`) reads `gallery.index` plus synchronized label/path numpy arrays.
- The `bundle/` directory is the single source of truth for artifacts, enabling reproducible, offline deployments.

## Getting Started Locally

### 1. Prerequisites
- Node.js ≥ 18
- Python ≥ 3.11
- (Optional) Docker + Docker Compose for containerized runs
- Access to the `bundle/` artifacts (model + index + gallery metadata)


### 2. Run the backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run the frontend/Node proxy
```bash
npm install
npm run dev   # or npm start
```
Visit `http://localhost:3001` and upload an image to test the workflow. The app will proxy API calls to `http://localhost:8000`.

### 4. Docker Compose (one command deployment)
```bash
docker compose up --build
```
This launches both containers, waits for the backend health check, and wires an internal bridge network so the Express proxy talks to FastAPI securely.

---

## Project Layout
- `public/` – static client (HTML/CSS/JS).
- `server.js` – Express static server + API proxy for local/dev deployments.
- `backend/` – FastAPI service, routes, models, and ML utilities.
- `bundle/` – model weights, FAISS index, and gallery metadata (not committed with assets).
- `docker-compose.yml` – orchestration of Node + FastAPI + shared Hugging Face cache.
- `pathUpdateModelNPY.py` – one time helper script for retargeting gallery path references after moving datasets.
