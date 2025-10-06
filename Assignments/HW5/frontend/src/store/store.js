import { configureStore } from '@reduxjs/toolkit';
import booksReducer from './booksSlice';
import chatReducer from './chatSlice';

export const store = configureStore({
  reducer: {
    books: booksReducer,
    chat: chatReducer,
  },
});