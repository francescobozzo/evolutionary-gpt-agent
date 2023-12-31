import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

type Experiment = {
  name: string;
  experiment_id: string;
  timestamp: string;
};

export function ExperimentListPage() {
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
      <Table sx={{ minWidth: 650 }} aria-label="experiment list table">
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
                <Link to={`/experiments/${experiment.experiment_id}`}>
                  {experiment.name}
                </Link>
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
