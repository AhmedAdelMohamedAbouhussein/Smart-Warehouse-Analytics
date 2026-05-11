/**
 * Smart Warehouse System — Type Definitions
 * Shared interfaces mirroring backend models for type safety.
 */

export type VelocityClass = 'A' | 'B' | 'C';

export interface Product {
  id: number;
  name: string;
  sku: string;
  width: number;
  height: number;
  depth: number;
  weight: number;
  velocity_class: VelocityClass;
  demand_frequency: number;
  current_stock: number;
  reorder_threshold: number;
  shelf_location: [number, number] | null;
}

export type OrderStatus = 'pending' | 'assigned' | 'picking' | 'completed' | 'cancelled';

export interface OrderItem {
  product_id: number;
  product_name: string;
  quantity: number;
  shelf_location: [number, number] | null;
}

export interface Order {
  id: number;
  status: OrderStatus;
  items: OrderItem[];
  assigned_picker_id: number | null;
  created_at: number;
  assigned_at: number | null;
  completed_at: number | null;
  total_distance: number;
  pick_route: [number, number][];
  optimized_route: [number, number][];
}

export type PickerStatus = 'idle' | 'traveling' | 'picking' | 'returning' | 'replenishing';

export interface Picker {
  id: number;
  name: string;
  status: PickerStatus;
  current_position: [number, number];
  home_station: [number, number];
  assigned_order_id: number | null;
  route: [number, number][];
  route_index: number;
  current_target: [number, number] | null;
  total_distance_traveled: number;
  orders_completed: number;
  total_idle_time: number;
  total_active_time: number;
  color: string;
}

export type CellType = 'path' | 'shelf' | 'pick_station' | 'receiving' | 'empty' | 'wall';

export interface WarehouseCell {
  row: number;
  col: number;
  cell_type: CellType;
  zone: 'A' | 'B' | 'C' | 'station' | 'receiving' | null;
  shelf_id: number | null;
  shelf_capacity: number;
  shelf_used: number;
  products: number[];
  visit_count: number;
}

export interface WarehouseLayout {
  rows: number;
  cols: number;
  grid: WarehouseCell[][];
}

export interface SimulationMetrics {
  total_distance: number;
  active_orders: number;
  completed_orders: number;
  pending_orders: number;
  idle_pickers: number;
  active_pickers: number;
  avg_utilization: number;
  avg_cycle_time: number;
  shelf_utilization: number;
  orders_per_minute: number;
}

export interface SimulationState {
  tick: number;
  running: boolean;
  paused: boolean;
  speed: number;
  layout: WarehouseLayout | null;
  products: Record<number, Product>;
  orders: Record<number, Order>;
  completed_orders_count: number;
  pickers: Record<number, Picker>;
  events: SimulationEvent[];
  replenishment: ReplenishmentState;
  metrics: SimulationMetrics;
  history: {
    ticks: number[];
    throughput: number[];
    utilization: number[];
  };
  heatmap: Record<string, number>;
}

export interface SimulationEvent {
  tick: number;
  time: number;
  type: string;
  message: string;
}

export interface ReplenishmentTask {
  id: number;
  product_id: number;
  product_name: string;
  status: 'active' | 'completed';
  source: [number, number];
  destination: [number, number];
  shelf_location: [number, number];
  quantity: number;
  route: [number, number][];
  route_index: number;
  distance: number;
  created_at: number;
  completed_at: number | null;
}

export interface ReplenishmentState {
  active_tasks: ReplenishmentTask[];
  completed_count: number;
  total_quantity_moved: number;
  total_distance: number;
}
