import { useParams } from 'react-router-dom';

export function BeliefsetPage() {
  const { id } = useParams();

  return <h1>Beliefset Page: {id}</h1>;
}
