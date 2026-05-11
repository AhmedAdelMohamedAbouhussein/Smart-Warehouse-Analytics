import { create } from 'zustand';
import { SimulationState, SimulationEvent } from '../types';

interface SimulationStore extends SimulationState {
  setInitialState: (state: SimulationState) => void;
  updateFromTick: (tickData: Partial<SimulationState>) => void;
  addEvent: (event: SimulationEvent) => void;
  setRunning: (running: boolean) => void;
  setPaused: (paused: boolean) => void;
  setSpeed: (speed: number) => void;
}

const initialState: SimulationState = {
  tick: 0,
  running: false,
  paused: false,
  speed: 1.0,
  layout: null,
  products: {},
  orders: {},
  completed_orders_count: 0,
  pickers: {},
  events: [],
  replenishment: {
    active_tasks: [],
    completed_count: 0,
    total_quantity_moved: 0,
    total_distance: 0,
  },
  metrics: {
    total_distance: 0,
    active_orders: 0,
    completed_orders: 0,
    pending_orders: 0,
    idle_pickers: 0,
    active_pickers: 0,
    avg_utilization: 0,
    avg_cycle_time: 0,
    shelf_utilization: 0,
    orders_per_minute: 0,
  },
  history: {
    ticks: [],
    throughput: [],
    utilization: []
  },
  heatmap: {},
};

export const useSimulationStore = create<SimulationStore>((set) => ({
  ...initialState,

  setInitialState: (state) => set({ ...state, history: initialState.history }),

  updateFromTick: (tickData) => set((state) => {
    const nextTick = tickData.tick || state.tick;
    let nextHistory = state.history;

    // Record history every 50 ticks
    if (nextTick > 0 && nextTick % 50 === 0 && nextTick !== state.history.ticks[state.history.ticks.length - 1]) {
      nextHistory = {
        ticks: [...state.history.ticks.slice(-19), nextTick],
        throughput: [...state.history.throughput.slice(-19), tickData.metrics?.orders_per_minute || 0],
        utilization: [...state.history.utilization.slice(-19), tickData.metrics?.avg_utilization || 0]
      };
    }

    return {
      ...state,
      ...tickData,
      history: nextHistory,
      products: tickData.products || state.products,
      orders: tickData.orders || state.orders,
      pickers: tickData.pickers || state.pickers,
      metrics: tickData.metrics || state.metrics,
      replenishment: tickData.replenishment || state.replenishment,
      events: tickData.events || state.events,
    };
  }),

  addEvent: (event) => set((state) => ({
    events: [...state.events.slice(-49), event],
  })),

  setRunning: (running) => set({ running }),
  setPaused: (paused) => set({ paused }),
  setSpeed: (speed) => set({ speed }),
}));
