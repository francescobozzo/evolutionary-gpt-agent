import {
  Box,
  Card,
  CardContent,
  Divider,
  Grid,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import Tree from 'react-d3-tree';
import { useParams } from 'react-router-dom';
import CustomNodeElement, {
  CustomNodeElementProps,
} from '../components/CustomNodeElement';

type Checkpoint = {
  id: number;
  type: string;
  // game_dump: any
  children: Checkpoint[];
};

type NodeDetail = {
  id: number;
  type: string;
};

export function CheckpointTreePage() {
  const { id: experiment_id } = useParams();
  const [checkpoints, setCheckpoints] = useState<Checkpoint>();
  const [nodeDetail, setNodeDetail] = useState<NodeDetail>();

  const refContainer = useRef<any>();
  const [dimensions, setDimensions] = useState({
    width: 0,
    height: 0,
  });
  useEffect(() => {
    if (refContainer.current) {
      setDimensions({
        width: refContainer.current.offsetWidth,
        height: refContainer.current.offsetHeight,
      });
    }
  }, [checkpoints]);

  useEffect(() => {
    fetch(`http://localhost:9876/checkpoints?experiment_id=${experiment_id}`)
      .then((res) => res.json())
      .then((data: Checkpoint) => setCheckpoints(data))
      .catch((err) => console.error(err));
    return () => {}; // cleanup function
  }, []);

  return checkpoints ? (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Card sx={{ m: 2 }}>
        <CardContent>
          <Typography variant="h6">
            Checkpoint History for Experiment {experiment_id}
          </Typography>
          <Box ref={refContainer}>
            <Tree
              data={checkpoints}
              collapsible={false}
              draggable={true}
              translate={{ x: dimensions.width / 2, y: dimensions.height / 2 }}
              enableLegacyTransition={true}
              onNodeClick={(node: any, _: any) => {
                setNodeDetail({
                  id: node.data.attributes.id,
                  type: node.data.attributes.type,
                });
              }}
              renderCustomNodeElement={(props: CustomNodeElementProps) => {
                return (
                  <CustomNodeElement
                    nodeDatum={props.nodeDatum}
                    hierarchyPointNode={props.hierarchyPointNode}
                    toggleNode={props.toggleNode}
                    onNodeClick={props.onNodeClick}
                    onNodeMouseOver={props.onNodeMouseOver}
                    onNodeMouseOut={props.onNodeMouseOut}
                    addChildren={props.addChildren}
                    isSelected={
                      nodeDetail?.id === props.nodeDatum.attributes.id
                    }
                  />
                );
              }}
            />
          </Box>
        </CardContent>
      </Card>
      <Divider />
      <Box flex={2} m={2}>
        {nodeDetail ? (
          <Card>
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="h6" component="div">
                    Checkpoint Details (selected node)
                  </Typography>
                </Grid>
                <Grid item xs={2}>
                  <TextField disabled label="Type" value={nodeDetail?.type} />
                </Grid>
                <Grid item xs={2}>
                  <TextField disabled label="ID" value={nodeDetail?.id} />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        ) : (
          'Select a Node...'
        )}
      </Box>
    </Box>
  ) : (
    'Loading...'
  );
}
