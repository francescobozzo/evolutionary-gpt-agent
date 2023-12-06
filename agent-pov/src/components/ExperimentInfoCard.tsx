import { Button, Card, CardActions, CardContent } from '@mui/material';
import Typography from '@mui/material/Typography';
import { Link } from 'react-router-dom';

interface ExperimentInfoCardProps {
  title: string;
  description: string;
  counter: number;
  linkToPage: string;
}

export default function ExperimentInfoCard(props: ExperimentInfoCardProps) {
  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent>
        <Typography variant="h5" component="div">
          {props.title}
        </Typography>
        <Typography sx={{ mb: 1.5 }} color="text.secondary">
          {props.description}
        </Typography>
        <Typography variant="body2">{props.counter}</Typography>
      </CardContent>
      <CardActions>
        <Button size="small">
          <Link to={props.linkToPage}>View</Link>
        </Button>
      </CardActions>
    </Card>
  );
}
