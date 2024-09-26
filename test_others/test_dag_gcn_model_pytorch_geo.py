import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, DenseGCNConv, dense_diff_pool
from torch_geometric.data import DataLoader

class GCN(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super(GCN, self).__init__()
        self.conv1 = GCNConv(in_channels, 64)
        self.conv2 = GCNConv(64, out_channels)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return x


class DiffPoolNet(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, num_classes, num_nodes=10):
        super(DiffPoolNet, self).__init__()
        self.gcn1 = GCN(in_channels, hidden_channels)
        self.gcn_pool = GCN(in_channels, num_nodes)
        self.gcn2 = DenseGCNConv(hidden_channels, hidden_channels)
        self.lin1 = torch.nn.Linear(hidden_channels, hidden_channels)
        self.lin2 = torch.nn.Linear(hidden_channels, num_classes)

    def forward(self, data):
        # Node features and adjacency matrix
        x, edge_index, batch = data.x, data.edge_index, data.batch

        # Step 1: Apply GCN to get node embeddings
        x = self.gcn1(x, edge_index)

        # Step 2: Apply DiffPool
        s = self.gcn_pool(x, edge_index)  # Soft assignment matrix for clustering
        x, adj, _, _ = dense_diff_pool(x, edge_index, s, batch)

        # Step 3: Apply another GCN layer on the coarsened graph
        x = self.gcn2(x, adj)

        # Step 4: Global pooling to get graph representation
        x = x.mean(dim=1)  # Global average pooling

        # Step 5: Classification
        x = F.relu(self.lin1(x))
        x = self.lin2(x)

        return F.log_softmax(x, dim=-1)

# Example dataset loader (using random graphs as placeholders)
from torch_geometric.datasets import TUDataset

dataset = TUDataset(root='/tmp/ENZYMES', name='ENZYMES')  # Example dataset
loader = DataLoader(dataset, batch_size=32, shuffle=True)

# Create the model, define the optimizer and loss function
model = DiffPoolNet(in_channels=dataset.num_node_features, hidden_channels=64, num_classes=6)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

# Training loop
for epoch in range(200):
    model.train()
    total_loss = 0
    for data in loader:
        optimizer.zero_grad()
        out = model(data)
        loss = F.nll_loss(out, data.y)
        loss.backward()
        total_loss += loss.item()
        optimizer.step()

    print(f'Epoch {epoch+1}, Loss: {total_loss/len(loader)}')





# ##########
# # EXAMPLE OF DAG REPRESENTATION USING PYTORCH GEOMETRIC
# ##########
# import torch
# from torch_geometric.data import Data

# # Node features (4 nodes, 3 features per node for demonstration)
# x = torch.tensor([[1, 2, 3],
#                   [4, 5, 6],
#                   [7, 8, 9],
#                   [10, 11, 12]], dtype=torch.float)

# # Directed edges (from, to)
# edge_index = torch.tensor([[0, 0, 1, 2],  # Source nodes
#                            [1, 2, 3, 3]], # Target nodes
#                            dtype=torch.long)

# # Create a PyTorch Geometric Data object
# data = Data(x=x, edge_index=edge_index)

# # Print the DAG structure
# print("Node features (x):\n", data.x)
# print("Directed edges (edge_index):\n", data.edge_index)
