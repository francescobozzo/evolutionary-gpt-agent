import {
  Box,
  Grid,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

type Beliefset = {
  belief_set_id: number;
  data: any;
  experiment_id: number;
};

export function BeliefsetPage() {
  const { id: experiment_id } = useParams();

  const [beliefsets, setBeliefsets] = useState<Beliefset[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  useEffect(() => {
    fetch(`http://localhost:9876/beliefsets?experiment_id=${experiment_id}`)
      .then((res) => res.json())
      .then((data: Beliefset[]) => setBeliefsets(data))
      .catch((err) => console.error(err));
    return () => {}; // cleanup function
  }, []);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Typography variant="h6" px={3} pt={3}>
          Beliefset for Experiment {experiment_id}
        </Typography>
      </Grid>

      <Grid item xs={3}>
        <List>
          {beliefsets.map((beliefset, index) => (
            <ListItem disablePadding key={beliefset.belief_set_id}>
              <ListItemButton selected={selectedIndex === index}>
                <ListItemText
                  primary={beliefset.belief_set_id}
                  onClick={() => {
                    setSelectedIndex(index);
                    console.log(JSON.stringify(beliefset.data, undefined, 4));
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Grid>
      <Grid item xs={9}>
        <Box height={'100vh'}>
          {selectedIndex ? (
            <SyntaxHighlighter language="json" showLineNumbers style={docco}>
              {JSON.stringify(beliefsets[selectedIndex].data, undefined, 4) ??
                '{}'}
            </SyntaxHighlighter>
          ) : null}
        </Box>
      </Grid>
    </Grid>
  );
}
