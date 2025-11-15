import { Post } from '../types';

const DB_NAME = 'HireMeBahamasDB';
const DB_VERSION = 1;
const POSTS_STORE = 'posts';
const PENDING_ACTIONS_STORE = 'pendingActions';
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export interface CachedPost extends Post {
  cachedAt: number;
}

export interface PendingAction {
  id: string;
  type: 'create' | 'update' | 'delete' | 'like' | 'comment';
  postId?: number;
  data: any;
  timestamp: number;
  retryCount: number;
}

class PostCache {
  private db: IDBDatabase | null = null;
  private initPromise: Promise<void> | null = null;

  constructor() {
    this.initPromise = this.initDB();
  }

  /**
   * Initialize IndexedDB
   */
  private async initDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('Failed to open IndexedDB:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Create posts store
        if (!db.objectStoreNames.contains(POSTS_STORE)) {
          const postsStore = db.createObjectStore(POSTS_STORE, { keyPath: 'id' });
          postsStore.createIndex('cachedAt', 'cachedAt', { unique: false });
        }

        // Create pending actions store
        if (!db.objectStoreNames.contains(PENDING_ACTIONS_STORE)) {
          const actionsStore = db.createObjectStore(PENDING_ACTIONS_STORE, { keyPath: 'id' });
          actionsStore.createIndex('timestamp', 'timestamp', { unique: false });
        }
      };
    });
  }

  /**
   * Ensure DB is initialized
   */
  private async ensureDB(): Promise<IDBDatabase> {
    if (this.db) {
      return this.db;
    }
    await this.initPromise;
    if (!this.db) {
      throw new Error('Failed to initialize database');
    }
    return this.db;
  }

  /**
   * Cache posts
   */
  async cachePosts(posts: Post[]): Promise<void> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([POSTS_STORE], 'readwrite');
      const store = transaction.objectStore(POSTS_STORE);

      const cachedPosts: CachedPost[] = posts.map(post => ({
        ...post,
        cachedAt: Date.now(),
      }));

      for (const post of cachedPosts) {
        store.put(post);
      }

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });
    } catch (error) {
      console.error('Failed to cache posts:', error);
    }
  }

  /**
   * Get cached posts
   */
  async getCachedPosts(): Promise<Post[]> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([POSTS_STORE], 'readonly');
      const store = transaction.objectStore(POSTS_STORE);

      const request = store.getAll();

      const cachedPosts = await new Promise<CachedPost[]>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });

      // Filter out expired cache
      const now = Date.now();
      const validPosts = cachedPosts.filter(
        post => now - post.cachedAt < CACHE_DURATION
      );

      // Remove cache timestamp before returning
      return validPosts.map(({ cachedAt, ...post }) => post);
    } catch (error) {
      console.error('Failed to get cached posts:', error);
      return [];
    }
  }

  /**
   * Update a single cached post
   */
  async updateCachedPost(postId: number, updates: Partial<Post>): Promise<void> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([POSTS_STORE], 'readwrite');
      const store = transaction.objectStore(POSTS_STORE);

      const request = store.get(postId);
      
      const post = await new Promise<CachedPost | undefined>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });

      if (post) {
        const updatedPost = { ...post, ...updates, cachedAt: Date.now() };
        store.put(updatedPost);

        await new Promise<void>((resolve, reject) => {
          transaction.oncomplete = () => resolve();
          transaction.onerror = () => reject(transaction.error);
        });
      }
    } catch (error) {
      console.error('Failed to update cached post:', error);
    }
  }

  /**
   * Delete cached post
   */
  async deleteCachedPost(postId: number): Promise<void> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([POSTS_STORE], 'readwrite');
      const store = transaction.objectStore(POSTS_STORE);

      store.delete(postId);

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });
    } catch (error) {
      console.error('Failed to delete cached post:', error);
    }
  }

  /**
   * Add pending action
   */
  async addPendingAction(action: Omit<PendingAction, 'id'>): Promise<string> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([PENDING_ACTIONS_STORE], 'readwrite');
      const store = transaction.objectStore(PENDING_ACTIONS_STORE);

      const id = `${action.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const pendingAction: PendingAction = { ...action, id };

      store.put(pendingAction);

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });

      return id;
    } catch (error) {
      console.error('Failed to add pending action:', error);
      throw error;
    }
  }

  /**
   * Get all pending actions
   */
  async getPendingActions(): Promise<PendingAction[]> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([PENDING_ACTIONS_STORE], 'readonly');
      const store = transaction.objectStore(PENDING_ACTIONS_STORE);

      const request = store.getAll();

      return await new Promise<PendingAction[]>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
    } catch (error) {
      console.error('Failed to get pending actions:', error);
      return [];
    }
  }

  /**
   * Remove pending action
   */
  async removePendingAction(id: string): Promise<void> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([PENDING_ACTIONS_STORE], 'readwrite');
      const store = transaction.objectStore(PENDING_ACTIONS_STORE);

      store.delete(id);

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });
    } catch (error) {
      console.error('Failed to remove pending action:', error);
    }
  }

  /**
   * Update retry count for pending action
   */
  async updatePendingActionRetry(id: string): Promise<void> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([PENDING_ACTIONS_STORE], 'readwrite');
      const store = transaction.objectStore(PENDING_ACTIONS_STORE);

      const request = store.get(id);
      
      const action = await new Promise<PendingAction | undefined>((resolve, reject) => {
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });

      if (action) {
        action.retryCount += 1;
        store.put(action);

        await new Promise<void>((resolve, reject) => {
          transaction.oncomplete = () => resolve();
          transaction.onerror = () => reject(transaction.error);
        });
      }
    } catch (error) {
      console.error('Failed to update pending action retry:', error);
    }
  }

  /**
   * Clear all cache
   */
  async clearCache(): Promise<void> {
    try {
      const db = await this.ensureDB();
      const transaction = db.transaction([POSTS_STORE, PENDING_ACTIONS_STORE], 'readwrite');
      
      transaction.objectStore(POSTS_STORE).clear();
      transaction.objectStore(PENDING_ACTIONS_STORE).clear();

      await new Promise<void>((resolve, reject) => {
        transaction.oncomplete = () => resolve();
        transaction.onerror = () => reject(transaction.error);
      });
    } catch (error) {
      console.error('Failed to clear cache:', error);
    }
  }

  /**
   * Check if cache is available
   */
  isCacheAvailable(): boolean {
    return 'indexedDB' in window;
  }
}

// Export singleton instance
export const postCache = new PostCache();
