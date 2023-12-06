import { useParams } from 'react-router-dom';

export function PlanListPage() {
  const { id: experiment_id } = useParams();

  return <div>TODO: plan list for experiment {experiment_id}</div>;
}
