import { useParams } from 'react-router-dom';

export function EventListPage() {
  const { id: experiment_id } = useParams();

  return <div>TODO: event list for experiment {experiment_id}</div>;
}
