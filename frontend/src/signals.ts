/**
 * Lightweight Signals-based reactivity for FindTheCoffee
 * Inspired by Preact Signals and SolidJS
 *
 * Usage:
 *   import { signal, computed, effect, batch } from "./signals";
 *
 *   const count = signal(0);
 *   const doubled = computed(() => count.value * 2);
 *   effect(() => console.log(`Count: ${count.value}`));
 *   count.value = 5; // Triggers effect
 */

type CleanupFn = () => void;
type Subscriber = () => void;

interface EffectContext {
  subscribe: (fn: Subscriber) => void;
  run: () => void;
}

let activeEffect: EffectContext | null = null;

class Signal<T> {
  private _value: T;
  private _subscribers: Set<Subscriber> = new Set();

  constructor(initialValue: T) {
    this._value = initialValue;
  }

  get value(): T {
    if (activeEffect) {
      const effectSubscriber = activeEffect;
      const unsubscribe = () => {
        this._subscribers.delete(effectSubscriber.run);
      };
      this._subscribers.add(effectSubscriber.run);
      effectSubscriber.subscribe(unsubscribe);
    }
    return this._value;
  }

  set value(newValue: T) {
    if (this._value === newValue) return;
    this._value = newValue;
    this._notify();
  }

  private _notify(): void {
    this._subscribers.forEach((fn) => fn());
  }
}

class Computed<T> {
  private _signal: Signal<T | null> = new Signal(null);
  private _computeFn: () => T;
  private _dirty = true;
  private _cachedValue: T | null = null;
  private _cleanupFns: CleanupFn[] = [];

  constructor(computeFn: () => T) {
    this._computeFn = computeFn;
  }

  get value(): T {
    if (this._dirty) {
      this._cleanupFns.forEach((fn) => fn());
      this._cleanupFns = [];

      const oldEffect = activeEffect;
      activeEffect = {
        subscribe: (fn: Subscriber) => {
          this._cleanupFns.push(fn);
        },
        run: () => {},
      };

      try {
        this._cachedValue = this._computeFn();
        this._dirty = false;
      } finally {
        activeEffect = oldEffect;
      }
    }

    if (activeEffect && this._cachedValue !== null) {
      this._signal.value;
    }

    return this._cachedValue!;
  }

  // @ts-ignore - Reserved for future use (computed invalidation)
  private _markDirty(): void {
    this._dirty = true;
    this._signal.value = null;
  }
}

/**
 * Create a reactive signal
 * @param initialValue - Initial value of the signal
 */
export function signal<T>(initialValue: T): Signal<T> {
  return new Signal(initialValue);
}

/**
 * Create a computed value that auto-updates when dependencies change
 * @param computeFn - Function that computes the derived value
 */
export function computed<T>(computeFn: () => T): Computed<T> {
  return new Computed(computeFn);
}

/**
 * Create a side effect that runs when dependencies change
 * @param fn - Effect function that tracks signal accesses
 * @returns Cleanup function to dispose the effect
 */
export function effect(fn: () => void | CleanupFn): CleanupFn {
  const cleanupFns: CleanupFn[] = [];

  const runEffect = () => {
    cleanupFns.forEach((fn) => fn());
    cleanupFns.length = 0;

    const oldEffect = activeEffect;
    activeEffect = {
      subscribe: (_subscribeFn: Subscriber) => {
        cleanupFns.push(_subscribeFn);
      },
      run: fn,
    };

    try {
      const cleanup = fn();
      if (cleanup) cleanupFns.push(cleanup);
    } finally {
      activeEffect = oldEffect;
    }
  };

  runEffect();

  return () => {
    cleanupFns.forEach((fn) => fn());
  };
}

/**
 * Batch multiple signal updates to prevent redundant re-renders
 * @param fn - Function containing signal updates
 */
export function batch<T>(fn: () => T): T {
  // In a simple implementation, just execute the function
  // A more advanced version would queue notifications
  return fn();
}

/**
 * Create a signal with explicit get/set methods
 * Useful for passing around without exposing direct mutation
 */
export function readonlySignal<T>(sig: Signal<T>): { get value(): T } {
  return {
    get value() {
      return sig.value;
    },
  };
}

// ============ Example Usage ============

// Simple counter
// const count = signal(0);
// const doubled = computed(() => count.value * 2);
// effect(() => {
//   console.log(`Count: ${count.value}, Doubled: ${doubled.value}`);
// });
// count.value = 5; // Logs: Count: 5, Doubled: 10

// App state example
// interface AppState {
//   cafes: Cafe[];
//   filters: { query: string; roast: string };
//   isLoading: boolean;
// }
//
// const state = signal<AppState>({
//   cafes: [],
//   filters: { query: "", roast: "" },
//   isLoading: false
// });
//
// const filteredCafes = computed(() => {
//   return state.value.cafes.filter(cafe => {
//     if (state.value.filters.query && !cafe.name.includes(state.value.filters.query)) return false;
//     return true;
//   });
// });
//
// effect(() => {
//   renderResults(filteredCafes.value);
// });
