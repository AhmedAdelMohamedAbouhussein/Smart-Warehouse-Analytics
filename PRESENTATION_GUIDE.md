# Smart Warehouse System - Project Presentation

This document contains a detailed, slide-by-slide outline for your project presentation. 

---

## Slide 1: Title Slide
**Project Title**: Smart Warehouse System
**Subtitle**: Optimizing Logistics through Advanced Computing Algorithms
**Presented by**: 
- Abdelrahman mostafa (231027174)
- Yassin eslam (231017683)
- Ahmed adel (231007728)
- Omar wael (231007796)
**Date**: May 12, 2026

---

## Slide 2: Project Overview & Objectives
**Goal**: Design an automated Warehouse Management System (WMS) to handle the complete product lifecycle.
**Key Focus Areas**:
- **Inbound Receiving**: Efficiently intake new inventory.
- **Slotting (Bin Packing)**: Optimizing where products are stored to minimize future travel.
- **Outbound Picking (TSP)**: Finding the shortest sequence to collect items.
- **Replenishment**: Automated restocking when inventory levels fall.
**The Challenge**: Storage location affects picking efficiency. High-velocity items must be near packing stations to reduce travel time.

---

## Slide 3: Warehouse Model
**Representation**:
- The warehouse is modeled as a **Spatial Graph**.
- **Nodes**: Shelf locations, pick stations, and packing docks.
- **Edges**: Aisle segments with travel-time weights.
- **Grid Layout**: 30x80 grid with clearly defined zones.

**[SCREENSHOT PLACEHOLDER: 2D Warehouse Floor Map]**

---

## Slide 4: Algorithm 1 - Dijkstra’s Algorithm
**Role**: Shortest-path navigation.
**How it's applied**:
- Used to find the minimum distance between any two points on the warehouse floor.
- Accounts for turns and aisle congestion by using weighted edges.
**Technical Detail**:
- Uses a **Min-Heap (Priority Queue)** for efficiency.
- Complexity: $O((V + E) \log V)$, ensuring real-time response as pickers move.

---

## Slide 5: Algorithm 2 - Bin Packing (Slotting Optimization)
**Role**: Product placement strategy.
**Logic**: 
- Each shelf is a "Bin" with a fixed capacity.
- Products are "Items" with volume and **Velocity** (demand frequency).
**The A/B/C Strategy**:
- **Class A (Top 20% Rank)**: Highest demand. Placed in zones closest to pick stations.
- **Class B (Next 30% Rank)**: Medium demand. Placed in mid-range zones.
- **Class C (Remaining 50%)**: Low demand. Placed in far zones.
**FFD Approach**: First-Fit Decreasing (items sorted by volume) ensures maximum shelf utilization.

**[SCREENSHOT PLACEHOLDER: Color-coded Slotting Plan (Red/Yellow/Green)]**

---

## Slide 6: Algorithm 3 - DP Pick Route Optimization
**Role**: Multi-order "Wave Picking" optimization.
**The Problem**: Given a batch of $k$ items, what is the shortest sequence to visit them? (Traveling Salesperson Problem).
**The Solution**: **Held-Karp Dynamic Programming**.
- **State**: `(visited_set, current_location)` - the minimum distance to visit a subset and end at a specific spot.
- **Memoization**: Uses a `memo` table to avoid redundant calculations.
- **Benefit**: Guaranteed to find the **Mathematically Optimal** route.

---

## Slide 7: Held-Karp vs. Greedy Nearest Neighbor
**Comparison**:
- **Greedy**: Always goes to the next closest item. Fast but can result in long "backtracking" treks.
- **Held-Karp (DP)**: Looks at the whole trip at once. Might walk further for the first item to save a lot of walking for the last three.
**Performance Gap**: DP typically reduces total walking distance by **10%–25%** compared to Greedy.

**[SCREENSHOT PLACEHOLDER: Side-by-side Pick Route Visualization]**

---

## Slide 8: Algorithm 4 - Greedy Order Assignment
**Role**: Real-time workload balancing.
**The Process**:
- As orders arrive, the system checks all available pickers.
- **Assignment Rule**: Assign the order to the picker with the shortest "distance to first item."
- **Efficiency**: Prevents "bottlenecks" where one picker has too many orders while others are idle.
- **Real-time Logic**: If no picker can fulfill the order within a specific time window, a new "picking wave" is triggered.

---

## Slide 9: Replenishment & Simulation
**Automation**:
- System monitors stock levels in real-time.
- If stock < **5 units**, a replenishment task is automatically triggered.
- Replenishment carts follow Dijkstra-optimized paths from Receiving to the target shelf.
**Simulation Engine**:
- Real-time ticker with WebSocket updates to the frontend.
- Animates multiple pickers simultaneously moving through the aisles.

**[SCREENSHOT PLACEHOLDER: Replenishment Log / Table]**

---

## Slide 10: Results & Picker Efficiency Dashboard
**Key Metrics Tracked**:
- **Total Orders Completed**: Success throughput.
- **Average Cycle Time**: Time from order creation to completion.
- **Average Utilization %**: Time spent picking vs. time spent idle.
- **Total Walking Distance**: Cumulative distance saved by Held-Karp DP.

**[SCREENSHOT PLACEHOLDER: Efficiency Dashboard Graphs]**

---

## Slide 11: Conclusion
- **Efficiency Gains**: By combining Rank-based Slotting (ABC) and Optimal TSP (Held-Karp), travel distance is minimized across the entire warehouse lifecycle.
- **Scalability**: The system handles real-time arrivals and dynamic assignments efficiently.
- **Future Work**: Implementing machine learning to predict demand spikes and pre-emptively replenish high-velocity items.

---

## Slide 12: Q&A
**Thank You!**
Questions?
