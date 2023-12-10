import React from 'react';
import ReactDOM from 'react-dom/client';
import {
  Route,
  RouterProvider,
  createBrowserRouter,
  createRoutesFromElements,
} from 'react-router-dom';
import App from './App.tsx';
import './global.css';
import { BeliefsetListPage } from './pages/BeliefsetListPage.tsx';
import { CheckpointTreePage } from './pages/CheckpointTreePage.tsx';
import { EventListPage } from './pages/EventListPage.tsx';
import { ExperimentDetailsPage } from './pages/ExperimentDetailsPage.tsx';
import { ExperimentListPage } from './pages/ExperimentListPage.tsx';
import { PerceiverListPage } from './pages/PerceiverListPage.tsx';
import { PlanListPage } from './pages/PlanListPage.tsx';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<App />}>
      <Route path="/" element={<ExperimentListPage />} />
      <Route path="experiments" element={<ExperimentListPage />} />
      <Route path="experiments/:id" element={<ExperimentDetailsPage />} />
      <Route path="experiments/:id/events" element={<EventListPage />} />
      <Route
        path="experiments/:id/beliefsets"
        element={<BeliefsetListPage />}
      />
      <Route
        path="experiments/:id/perceivers"
        element={<PerceiverListPage />}
      />
      <Route path="experiments/:id/plans" element={<PlanListPage />} />
      <Route
        path="experiments/:id/checkpoints"
        element={<CheckpointTreePage />}
      />
    </Route>,
  ),
);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
