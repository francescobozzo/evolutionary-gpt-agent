import { CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import BeliefsetDetailsCard from '../components/BeliefsetDetailsCard';
import { FilterCenterFocusSharp } from '@mui/icons-material';

type Beliefset = {
  belief_set_id: number;
  data: any;
  experiment_id: number;
  representation: any;
};

function updateBeliefSet(
  data: any,
  belief_set_id: string | undefined,
  setter: any,
) {
  if (data.computing === false) {
    fetchBeliefSet(belief_set_id, setter);
  }
}

function fetchBeliefSet(belief_set_id: string | undefined, setter: any) {
  fetch(`http://localhost:9876/beliefsets/${belief_set_id}`)
    .then((res) => res.json())
    .then((data: Beliefset) => setter(data))
    .catch((err) => console.error(err));
}

export function BeliefsetDetailsPage() {
  const { id: belief_set_id } = useParams();

  const [beliefset, setBeliefset] = useState<Beliefset>();

  useEffect(() => {
    fetchBeliefSet(belief_set_id, setBeliefset);
    return () => {}; // cleanup function
  }, []);

  const generateRepresentation = (finalizeFunc: () => void) => {
    fetch(`http://localhost:9876/beliefsets/${belief_set_id}/representation`)
      .then((res) => res.json())
      .then((data) =>
        data.ready
          ? () => {
              finalizeFunc();
              fetchBeliefSet(belief_set_id, setBeliefset);
            }
          : () => {},
      )
      .catch((err) => console.error(err));
    return () => {};
  };

  return (
    <>
      <Typography variant="h4" component="div" textAlign={'center'} my={2}>
        Beliefset {belief_set_id} for experiment {beliefset?.experiment_id}
      </Typography>
      <Stack spacing={2} mx={4}>
        <BeliefsetDetailsCard
          title={'Data'}
          data={beliefset?.data}
          representation={beliefset?.representation}
          generateRepresentationCallback={generateRepresentation}
        />
      </Stack>
    </>
  );
}
