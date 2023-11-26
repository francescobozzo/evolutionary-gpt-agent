import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './global.css';
import {
  Route,
  RouterProvider,
  createBrowserRouter,
  createRoutesFromElements,
} from 'react-router-dom';
import { BeliefsetPage } from './pages/BeliefsetPage.tsx';
import { ExperimentPage } from './pages/ExperimentPage.tsx';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<App />}>
      <Route path="experiments" element={<ExperimentPage />} />
      <Route path="experiments/:id/beliefsets" element={<BeliefsetPage />} />
    </Route>,
  ),
);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
