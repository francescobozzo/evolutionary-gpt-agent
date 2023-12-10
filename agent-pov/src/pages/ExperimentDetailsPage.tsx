import { CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import ExperimentInfoCard from '../components/ExperimentInfoCard';

type ExperimentDetail = {
  name: string;
  experiment_id: string;
  timestamp: string;
  num_events: number;
  num_beliefsets: number;
  num_perceivers: number;
  num_plans: number;
};

export function ExperimentDetailsPage() {
  const { id: experiment_id } = useParams();
  const [experimentDetails, setExperimentDetails] =
    useState<ExperimentDetail>();

  useEffect(() => {
    fetch(`http://localhost:9876/experiments/${experiment_id}`)
      .then((res) => res.json())
      .then((data: ExperimentDetail) => setExperimentDetails(data))
      .catch((err) => console.error(err));
    return () => {}; // cleanup function
  }, []);

  return experimentDetails ? (
    <>
      <Typography variant="h4" component="div" textAlign={'center'} my={2}>
        Experiment {experiment_id}
      </Typography>
      <Stack spacing={2} mx={4}>
        <ExperimentInfoCard
          title={'Events'}
          description={
            'Number of received and processed events from the environment'
          }
          counter={experimentDetails?.num_events}
          linkToPage={`/experiments/${experiment_id}/events`}
        />
        <ExperimentInfoCard
          title={'Beliefsets'}
          description={'Number of processed beliefsets'}
          counter={experimentDetails?.num_beliefsets}
          linkToPage={`/experiments/${experiment_id}/beliefsets`}
        />
        <ExperimentInfoCard
          title={'Perceivers'}
          description={
            'Number of generated perceivers that processed input events'
          }
          counter={experimentDetails?.num_perceivers}
          linkToPage={`/experiments/${experiment_id}/perceivers`}
        />
        <ExperimentInfoCard
          title={'Plans'}
          description={
            'Number of generated plans that have been executed successfully'
          }
          counter={experimentDetails?.num_plans}
          linkToPage={`/experiments/${experiment_id}/plans`}
        />
        <ExperimentInfoCard
          title={'Checkpoints'}
          description={'Checkpoints Tree'}
          counter={-1}
          linkToPage={`/experiments/${experiment_id}/checkpoints`}
        />
      </Stack>
    </>
  ) : (
    <CircularProgress />
  );
}
