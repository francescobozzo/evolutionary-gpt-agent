/**
 * Sources:
 * - https://github.com/bkrem/react-d3-tree/blob/master/src/types/common.ts
 * - https://github.com/bkrem/react-d3-tree/blob/master/src/Node/DefaultNodeElement.tsx
 * - https://github.com/bkrem/react-d3-tree/blob/e67115aff35dfc77cfedfad0f17f65f89d716ef9/src/globalCss.ts#L27
 */

export interface CustomNodeElementProps {
  /**
   * The full datum of the node that is being rendered.
   */
  nodeDatum: {
    attributes: Record<string, string | number | boolean>;
    children: any;
    name: string;
  };
  /**
   * The D3 `HierarchyPointNode` representation of the node, which wraps `nodeDatum`
   * with additional properties.
   */
  hierarchyPointNode: any;
  /**
   * Toggles the expanded/collapsed state of the node.
   *
   * Provided for customized control flow; e.g. if we want to toggle the node when its
   * label is clicked instead of the node itself.
   */
  toggleNode: () => void;
  /**
   * The `onNodeClick` handler defined for `Tree` (if any).
   */
  onNodeClick: any;
  /**
   * The `onNodeMouseOver` handler defined for `Tree` (if any).
   */
  onNodeMouseOver: any;
  /**
   * The `onNodeMouseOut` handler defined for `Tree` (if any).
   */
  onNodeMouseOut: any;
  /**
   * The `Node` class's internal `addChildren` handler.
   */
  addChildren: any;
  /**
   * NEW: The `Node` class's internal `addChildren` handler.
   */
  isSelected: boolean;
}

const DEFAULT_NODE_CIRCLE_RADIUS = 15;

const textLayout = {
  title: {
    textAnchor: 'start',
    x: 40,
  },
  attribute: {
    x: 40,
    dy: '1.2em',
  },
};

const CustomNodeElement = ({
  nodeDatum,
  toggleNode,
  onNodeClick,
  onNodeMouseOver,
  onNodeMouseOut,
  isSelected,
}: CustomNodeElementProps) => {
  return (
    <>
      <circle
        r={DEFAULT_NODE_CIRCLE_RADIUS}
        onClick={(evt) => {
          toggleNode();
          onNodeClick(evt);
        }}
        onMouseOver={onNodeMouseOver}
        onMouseOut={onNodeMouseOut}
        className={isSelected ? 'rd3t-node' : 'rd3t-leaf-node'} // Edited
      ></circle>
      <g className="rd3t-label">
        <text className="rd3t-label__title" {...textLayout.title}>
          {nodeDatum.name}
        </text>
        <text className="rd3t-label__attributes">
          {nodeDatum.attributes &&
            Object.entries(nodeDatum.attributes).map(
              ([labelKey, labelValue], i) => (
                <tspan key={`${labelKey}-${i}`} {...textLayout.attribute}>
                  {labelKey}:{' '}
                  {typeof labelValue === 'boolean'
                    ? labelValue.toString()
                    : labelValue}
                </tspan>
              ),
            )}
        </text>
      </g>
    </>
  );
};

export default CustomNodeElement;
