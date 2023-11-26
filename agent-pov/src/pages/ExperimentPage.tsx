import { useEffect, useState } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';

type Experiment = {
  name: string;
  experiment_id: string;
  timestamp: string;
};

export function ExperimentPage() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);

  useEffect(() => {
    fetch('http://localhost:9876/experiments/')
      .then((res) => res.json())
      .then((data: Experiment[]) => setExperiments(data))
      .catch((err) => console.error(err));
    return () => {}; // cleanup function
  }, []);

  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 650 }} aria-label="simple table">
        <TableHead>
          <TableRow>
            <TableCell>Experiment</TableCell>
            <TableCell align="right">ID</TableCell>
            <TableCell align="right">Timestamp</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {experiments.map((experiment) => (
            <TableRow
              key={experiment.name}
              sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
            >
              <TableCell component="th" scope="row">
                {experiment.name}
              </TableCell>
              <TableCell align="right">{experiment.experiment_id}</TableCell>
              <TableCell align="right">{experiment.timestamp}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
