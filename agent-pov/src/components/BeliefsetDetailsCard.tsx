import {
  Button,
  Card,
  CardActions,
  CardContent,
  Box,
  Stack,
  CircularProgress,
} from '@mui/material';
import Typography from '@mui/material/Typography';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

import { useRef, useState, useEffect } from 'react';

interface BeliefsetDetailsCardProps {
  title: string;
  data: any;
  representation: any;
  generateRepresentationCallback: () => () => void;
}

export default function BeliefsetDetailsCard(props: BeliefsetDetailsCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  const [codeHighlightHeight, setCodeHighlightHeight] = useState<number>(0);
  const [isComputingRepresentation, setIsComputingRepresentation] =
    useState<boolean>(false);

  useEffect(() => {
    setCodeHighlightHeight(
      cardRef.current ? cardRef.current.clientHeight : 300,
    );
  });

  const fetchRepresentation = () => {
    setIsComputingRepresentation(true);
    props.generateRepresentationCallback();
    setIsComputingRepresentation(false);
  };

  return (
    <>
      <Stack spacing={2} mx={4}>
        <Typography variant="h5" component="div">
          {props.title}
        </Typography>
        <SyntaxHighlighter
          language="json"
          showLineNumbers
          style={docco}
          customStyle={{ maxHeight: 500 }}
        >
          {JSON.stringify(props.data, undefined, 4) ?? '{}'}
        </SyntaxHighlighter>
        {props.representation ? (
          <img src={`data:image/png;base64, ${props.representation}`} />
        ) : (
          <Box sx={{ m: 1, position: 'relative', alignItems: 'center' }}>
            <CircularProgress
              size={24}
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                marginTop: '-9px',
                marginLeft: '-12px',
              }}
            />
            <Button
              variant="contained"
              size="small"
              sx={{
                position: 'absolute',
                top: '50%',
                left: 'calc(50% - 12.5%)',
                marginTop: '-12px',
                marginLeft: '-12px',
              }}
              disabled={isComputingRepresentation}
              onClick={() => fetchRepresentation()}
            >
              Generate representation
            </Button>
          </Box>
        )}
      </Stack>
    </>
  );
}
