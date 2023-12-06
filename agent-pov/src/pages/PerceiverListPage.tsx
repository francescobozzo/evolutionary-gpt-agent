import { useParams } from 'react-router-dom';

export function PerceiverListPage() {
  const { id: experiment_id } = useParams();

  return <div>TODO: perceiver list for experiment {experiment_id}</div>;
}
