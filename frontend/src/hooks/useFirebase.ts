/**
 * React Hooks for Firebase Realtime Database
 * 
 * These hooks provide easy integration with Firebase Realtime Database
 * for real-time data synchronization in React components.
 */

import { useState, useEffect, useCallback } from 'react';
import {
  ref,
  onValue,
  set,
  update,
  push,
  remove,
  query,
  orderByChild,
  limitToLast,
  DataSnapshot,
} from 'firebase/database';
import { getFirebaseDatabase, isFirebaseAvailable } from '../config/firebase';

/**
 * Normalize Firebase path to prevent double slashes
 * @param parts - Path parts to join
 * @returns Normalized path
 */
const normalizePath = (...parts: string[]): string => {
  return parts
    .map((part, index) => {
      // Remove leading slash from all parts except the first
      if (index > 0 && part.startsWith('/')) {
        part = part.slice(1);
      }
      // Remove trailing slash from all parts except the last
      if (index < parts.length - 1 && part.endsWith('/')) {
        part = part.slice(0, -1);
      }
      return part;
    })
    .join('/');
};

/**
 * Hook to read data from Firebase Realtime Database
 * @param path - Database path to read from
 * @returns Object containing data, loading state, and error
 */
export const useFirebaseData = <T = any>(path: string) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!isFirebaseAvailable()) {
      setError(new Error('Firebase is not configured'));
      setLoading(false);
      return;
    }

    const database = getFirebaseDatabase();
    if (!database) {
      setError(new Error('Firebase database not available'));
      setLoading(false);
      return;
    }

    const dataRef = ref(database, path);
    
    const unsubscribe = onValue(
      dataRef,
      (snapshot: DataSnapshot) => {
        setData(snapshot.val());
        setLoading(false);
        setError(null);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [path]);

  return { data, loading, error };
};

/**
 * Hook to write data to Firebase Realtime Database
 * @param path - Database path to write to
 * @returns Object containing write functions and loading state
 */
export const useFirebaseWrite = (path: string) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const database = getFirebaseDatabase();

  const writeData = useCallback(
    async (data: any) => {
      if (!isFirebaseAvailable() || !database) {
        setError(new Error('Firebase is not configured'));
        return false;
      }

      setLoading(true);
      setError(null);

      try {
        const dataRef = ref(database, path);
        await set(dataRef, data);
        setLoading(false);
        return true;
      } catch (err) {
        setError(err as Error);
        setLoading(false);
        return false;
      }
    },
    [database, path]
  );

  const updateData = useCallback(
    async (updates: Record<string, any>) => {
      if (!isFirebaseAvailable() || !database) {
        setError(new Error('Firebase is not configured'));
        return false;
      }

      setLoading(true);
      setError(null);

      try {
        const dataRef = ref(database, path);
        await update(dataRef, updates);
        setLoading(false);
        return true;
      } catch (err) {
        setError(err as Error);
        setLoading(false);
        return false;
      }
    },
    [database, path]
  );

  const pushData = useCallback(
    async (data: any) => {
      if (!isFirebaseAvailable() || !database) {
        setError(new Error('Firebase is not configured'));
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        const dataRef = ref(database, path);
        const newRef = await push(dataRef, data);
        setLoading(false);
        return newRef.key;
      } catch (err) {
        setError(err as Error);
        setLoading(false);
        return null;
      }
    },
    [database, path]
  );

  const deleteData = useCallback(async () => {
    if (!isFirebaseAvailable() || !database) {
      setError(new Error('Firebase is not configured'));
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      const dataRef = ref(database, path);
      await remove(dataRef);
      setLoading(false);
      return true;
    } catch (err) {
      setError(err as Error);
      setLoading(false);
      return false;
    }
  }, [database, path]);

  return {
    writeData,
    updateData,
    pushData,
    deleteData,
    loading,
    error,
  };
};

/**
 * Hook to query Firebase Realtime Database with ordering and limiting
 * @param path - Database path to query
 * @param orderBy - Field to order by
 * @param limit - Maximum number of results
 * @returns Object containing queried data, loading state, and error
 */
export const useFirebaseQuery = <T = any>(
  path: string,
  orderBy: string,
  limit?: number
) => {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!isFirebaseAvailable()) {
      setError(new Error('Firebase is not configured'));
      setLoading(false);
      return;
    }

    const database = getFirebaseDatabase();
    if (!database) {
      setError(new Error('Firebase database not available'));
      setLoading(false);
      return;
    }

    const dataRef = ref(database, path);
    let dataQuery = query(dataRef, orderByChild(orderBy));
    
    if (limit) {
      dataQuery = query(dataQuery, limitToLast(limit));
    }

    const unsubscribe = onValue(
      dataQuery,
      (snapshot: DataSnapshot) => {
        const results: T[] = [];
        snapshot.forEach((child) => {
          results.push({ key: child.key, ...child.val() } as T);
        });
        setData(results);
        setLoading(false);
        setError(null);
      },
      (err) => {
        setError(err);
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [path, orderBy, limit]);

  return { data, loading, error };
};

/**
 * Hook to listen to a specific child in Firebase Realtime Database
 * @param path - Database path
 * @param childKey - Specific child key to listen to
 * @returns Object containing child data, loading state, and error
 */
export const useFirebaseChild = <T = any>(path: string, childKey: string) => {
  const fullPath = normalizePath(path, childKey);
  return useFirebaseData<T>(fullPath);
};
