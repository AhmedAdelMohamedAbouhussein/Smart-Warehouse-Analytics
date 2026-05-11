# Smart Warehouse System — AI-Powered Logistics Simulation

![Version](https://img.shields.io/badge/version-1.0.0-emerald)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.9+-yellow)
![React](https://img.shields.io/badge/React-18.0-cyan)

A high-performance, real-time warehouse management and simulation system built to solve the "last-yard" delivery challenge in fulfillment centers. This project implements advanced computer algorithms to optimize product slotting, picker routing, and real-time order assignment.

---

## 🚀 Core Algorithmic Implementation

This system is built around four primary algorithmic pillars, each solving a critical bottleneck in warehouse operations:

### 1. Product Slotting (Optimization: Bin Packing)
*   **Problem**: How to assign 100+ unique SKUs to limited shelf space based on demand velocity.
*   **Solution**: Implements a **Heuristic Bin Packing** algorithm combined with **ABC Classification**.
*   **Logic**: Class A products (high demand) are packed into shelves nearest to the pack stations (Zone A), while Class C products are slotted in the back (Zone C).

### 2. Global Pathfinding (Algorithm: Dijkstra)
*   **Problem**: Finding the shortest navigable path through a complex grid of aisles and obstacles.
*   **Solution**: A weighted **Dijkstra’s Algorithm** that converts the warehouse layout into a directed graph.
*   **Feature**: Includes "Turn Penalties" and "Congestion Weights" to simulate realistic travel times where robots slow down during cornering.

### 3. Route Optimization (Algorithm: Held-Karp / DP)
*   **Problem**: The "Traveling Salesperson Problem" (TSP) for multi-item orders.
*   **Solution**: Implements the **Held-Karp algorithm** using Dynamic Programming.
*   **Efficiency**: Reduces picker travel distance by up to 40% compared to a simple greedy visit order by calculating the optimal sequence of stops for every batch.

### 4. Real-Time Assignment (Heuristic: Greedy Assignment)
*   **Problem**: Assigning incoming orders to a fleet of 8+ robots in real-time.
*   **Solution**: A **Greedy Proximity Heuristic** that calculates the cost (distance) for each idle picker to reach the first item of an order and assigns the lowest-cost robot immediately.

---

## 🛠 Tech Stack

*   **Backend**: FastAPI (Python 3.9+) - High-concurrency async server.
*   **Frontend**: React + TypeScript + TailwindCSS - Premium, dark-mode analytical dashboard.
*   **Real-time Sync**: WebSockets (Bi-directional) - 200ms tick-based state broadcasting.
*   **Data Viz**: Recharts - Live throughput and utilization telemetry.
*   **Pathfinding**: Custom Graph implementation with `heapq` optimized Dijkstra.

---

## 📊 Analytics & Telemetry

The system provides a comprehensive "Operational Command Center":
*   **Throughput Trend**: Real-time tracking of "Orders per Minute."
*   **Picker Efficiency**: Individual robot utilization percentages and shift distance tracking.
*   **Replenishment Log**: Automated triggers for stock-outs with route logging.
*   **Heatmap Visualization**: Identifies high-traffic bottlenecks in the warehouse aisles.

---

## 📦 Installation & Setup

### Prerequisites
*   Python 3.9+
*   Node.js 18+
*   npm or yarn

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🎓 Academic Context
This project was developed for the **Computer Algorithms** module. It demonstrates the practical application of Graph Theory, Dynamic Programming, and Heuristic Search in a real-world industrial context.

**Key Deliverables Met:**
- [x] Weighted Directed Graph Construction
- [x] Shortest Path (Dijkstra) Integration
- [x] TSP Optimization (Held-Karp)
- [x] Operational Efficiency Dashboard
- [x] Live Replenishment Logging

---

## 📄 License
MIT License. Created by [Your Name/Group].
