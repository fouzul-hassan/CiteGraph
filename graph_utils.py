"""
Graph utilities module for CiteGraph
Handles citation graph building and visualization using NetworkX and pyvis
"""

import networkx as nx
import json
from typing import Dict, List, Optional, Tuple
import streamlit as st
from pyvis.network import Network
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


class CitationGraphBuilder:
    """Builds and manages citation graphs using NetworkX"""
    
    def __init__(self):
        """Initialize the graph builder"""
        self.graph = nx.DiGraph()
        self.node_data = {}
        self.edge_data = {}
    
    def build_graph_from_data(self, graph_data: Dict) -> nx.DiGraph:
        """Build NetworkX graph from citation data"""
        self.graph.clear()
        self.node_data = {}
        self.edge_data = {}
        
        # Add nodes
        for node in graph_data.get('nodes', []):
            node_id = node['id']
            self.graph.add_node(node_id)
            self.node_data[node_id] = node
        
        # Add edges
        for edge in graph_data.get('edges', []):
            from_node = edge['from']
            to_node = edge['to']
            if from_node in self.node_data and to_node in self.node_data:
                self.graph.add_edge(from_node, to_node)
                self.edge_data[(from_node, to_node)] = edge
        
        return self.graph
    
    def get_graph_statistics(self) -> Dict:
        """Get comprehensive graph statistics"""
        if not self.graph.nodes():
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'density': 0,
                'diameter': 0,
                'avg_clustering': 0,
                'connected_components': 0
            }
        
        try:
            # Basic stats
            total_nodes = self.graph.number_of_nodes()
            total_edges = self.graph.number_of_edges()
            
            # Calculate density
            density = nx.density(self.graph) if total_nodes > 1 else 0
            
            # Calculate diameter (for connected components)
            try:
                diameter = nx.diameter(self.graph.to_undirected())
            except:
                diameter = 0
            
            # Calculate clustering coefficient
            try:
                avg_clustering = nx.average_clustering(self.graph.to_undirected())
            except:
                avg_clustering = 0
            
            # Count connected components
            connected_components = nx.number_strongly_connected_components(self.graph)
            
            return {
                'total_nodes': total_nodes,
                'total_edges': total_edges,
                'density': round(density, 4),
                'diameter': diameter,
                'avg_clustering': round(avg_clustering, 4),
                'connected_components': connected_components
            }
            
        except Exception as e:
            print(f"Error calculating graph statistics: {e}")
            return {
                'total_nodes': len(self.graph.nodes()),
                'total_edges': len(self.graph.edges()),
                'density': 0,
                'diameter': 0,
                'avg_clustering': 0,
                'connected_components': 0
            }
    
    def get_centrality_measures(self) -> Dict:
        """Calculate centrality measures for nodes"""
        if not self.graph.nodes():
            return {}
        
        try:
            # In-degree centrality (how many papers cite this one)
            in_degree_centrality = nx.in_degree_centrality(self.graph)
            
            # Out-degree centrality (how many papers this one cites)
            out_degree_centrality = nx.out_degree_centrality(self.graph)
            
            # Betweenness centrality (how important as a bridge)
            try:
                betweenness_centrality = nx.betweenness_centrality(self.graph)
            except:
                betweenness_centrality = {node: 0 for node in self.graph.nodes()}
            
            # PageRank (importance based on connections)
            try:
                pagerank = nx.pagerank(self.graph)
            except:
                pagerank = {node: 1/len(self.graph.nodes()) for node in self.graph.nodes()}
            
            return {
                'in_degree': in_degree_centrality,
                'out_degree': out_degree_centrality,
                'betweenness': betweenness_centrality,
                'pagerank': pagerank
            }
            
        except Exception as e:
            print(f"Error calculating centrality measures: {e}")
            return {}
    
    def get_community_clusters(self) -> Dict:
        """Detect community clusters in the citation graph"""
        if not self.graph.nodes():
            return {}
        
        try:
            # Convert to undirected graph for community detection
            undirected_graph = self.graph.to_undirected()
            
            # Use Louvain method for community detection
            try:
                from community import community_louvain
                communities = community_louvain.best_partition(undirected_graph)
            except ImportError:
                # Fallback to label propagation
                communities = nx.community.label_propagation_communities(undirected_graph)
                # Convert to node->community mapping
                community_map = {}
                for i, community in enumerate(communities):
                    for node in community:
                        community_map[node] = i
                communities = community_map
            
            # Group nodes by community
            community_groups = {}
            for node, community_id in communities.items():
                if community_id not in community_groups:
                    community_groups[community_id] = []
                community_groups[community_id].append(node)
            
            return {
                'communities': communities,
                'community_groups': community_groups,
                'num_communities': len(community_groups)
            }
            
        except Exception as e:
            print(f"Error detecting communities: {e}")
            return {}
    
    def filter_graph_by_year(self, start_year: int, end_year: int) -> nx.DiGraph:
        """Filter graph to include only papers within a year range"""
        filtered_graph = self.graph.copy()
        
        nodes_to_remove = []
        for node in filtered_graph.nodes():
            node_data = self.node_data.get(node, {})
            year = node_data.get('year', 0)
            if year < start_year or year > end_year:
                nodes_to_remove.append(node)
        
        filtered_graph.remove_nodes_from(nodes_to_remove)
        return filtered_graph
    
    def filter_graph_by_citation_count(self, min_citations: int) -> nx.DiGraph:
        """Filter graph to include only papers with minimum citation count"""
        filtered_graph = self.graph.copy()
        
        nodes_to_remove = []
        for node in filtered_graph.nodes():
            node_data = self.node_data.get(node, {})
            citation_count = node_data.get('citation_count', 0)
            if citation_count < min_citations:
                nodes_to_remove.append(node)
        
        filtered_graph.remove_nodes_from(nodes_to_remove)
        return filtered_graph


class CitationGraphVisualizer:
    """Visualizes citation graphs using pyvis and Plotly"""
    
    def __init__(self):
        """Initialize the visualizer"""
        self.network = None
    
    def create_interactive_network(self, graph_data: Dict, height: str = "600px") -> str:
        """Create an interactive network visualization using pyvis"""
        try:
            # Create pyvis network
            net = Network(height=height, width="100%", bgcolor="#ffffff", font_color="#000000")
            
            # Add nodes
            for node in graph_data.get('nodes', []):
                node_id = node['id']
                label = node.get('label', node_id)
                title = node.get('title', '')
                year = node.get('year', '')
                citation_count = node.get('citation_count', 0)
                group = node.get('group', 'default')
                
                # Set node properties based on group
                if group == 'root':
                    color = '#e74c3c'
                    size = 25
                elif group == 'citation':
                    color = '#3498db'
                    size = 20
                elif group == 'reference':
                    color = '#f39c12'
                    size = 20
                elif group == 'related':
                    color = '#00b894'
                    size = 18
                elif group == 'expanded_citation':
                    color = '#9b59b6'
                    size = 18
                elif group == 'most_relevant':
                    color = '#f1c40f'
                    size = 22
                else:
                    color = '#95a5a6'
                    size = 15
                
                # Create hover title
                hover_title = f"Title: {title}\nYear: {year}\nCitations: {citation_count}"
                
                net.add_node(
                    node_id, 
                    label=label, 
                    title=hover_title,
                    color=color,
                    size=size
                )
            
            # Add edges
            for edge in graph_data.get('edges', []):
                from_node = edge['from']
                to_node = edge['to']
                color = edge.get('color', '#2c3e50')
                arrows = edge.get('arrows', 'to')
                dashes = edge.get('dashes', False)
                
                net.add_edge(
                    from_node, 
                    to_node, 
                    color=color,
                    arrows=arrows,
                    width=2,
                    dashes=dashes
                )
            
            # Configure physics
            net.set_options("""
            var options = {
              "physics": {
                "forceAtlas2Based": {
                  "gravitationalConstant": -50,
                  "centralGravity": 0.01,
                  "springLength": 100,
                  "springConstant": 0.08
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
              }
            }
            """)
            
            # Save to HTML string
            html_string = net.generate_html()
            return html_string
            
        except Exception as e:
            print(f"Error creating interactive network: {e}")
            return f"<p>Error creating visualization: {e}</p>"
    
    def create_timeline_chart(self, timeline_data: Dict) -> go.Figure:
        """Create a timeline chart showing knowledge evolution"""
        try:
            years = timeline_data.get('years', [])
            counts = timeline_data.get('counts', [])
            
            if not years or not counts:
                # Return empty chart
                fig = go.Figure()
                fig.add_annotation(
                    text="No timeline data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            # Create the timeline chart
            fig = go.Figure()
            
            # Add bar chart
            fig.add_trace(go.Bar(
                x=years,
                y=counts,
                name='Papers per Year',
                marker_color='#3498db',
                hovertemplate='<b>Year:</b> %{x}<br>' +
                            '<b>Papers:</b> %{y}<br>' +
                            '<extra></extra>'
            ))
            
            # Add line connecting the bars
            fig.add_trace(go.Scatter(
                x=years,
                y=counts,
                mode='lines+markers',
                name='Trend',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=8, color='#e74c3c'),
                hovertemplate='<b>Year:</b> %{x}<br>' +
                            '<b>Papers:</b> %{y}<br>' +
                            '<extra></extra>'
            ))
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Knowledge Evolution Timeline',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                },
                xaxis_title='Year',
                yaxis_title='Number of Papers',
                hovermode='x unified',
                showlegend=True,
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating timeline chart: {e}")
            # Return error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating timeline: {e}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_citation_distribution_chart(self, graph_data: Dict) -> go.Figure:
        """Create a chart showing distribution of citation counts"""
        try:
            citation_counts = []
            for node in graph_data.get('nodes', []):
                count = node.get('citation_count', 0)
                if count > 0:
                    citation_counts.append(count)
            
            if not citation_counts:
                # Return empty chart
                fig = go.Figure()
                fig.add_annotation(
                    text="No citation data available",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
                return fig
            
            # Create histogram
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=citation_counts,
                nbinsx=20,
                name='Citation Distribution',
                marker_color='#9b59b6',
                opacity=0.7,
                hovertemplate='<b>Citations:</b> %{x}<br>' +
                            '<b>Count:</b> %{y}<br>' +
                            '<extra></extra>'
            ))
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Distribution of Citation Counts',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20}
                },
                xaxis_title='Number of Citations',
                yaxis_title='Number of Papers',
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating citation distribution chart: {e}")
            # Return error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating distribution chart: {e}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_network_metrics_dashboard(self, graph_stats: Dict, centrality_data: Dict) -> go.Figure:
        """Create a dashboard showing network metrics"""
        try:
            # Create subplots
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Network Overview', 'Centrality Distribution', 
                              'Top Cited Papers', 'Network Properties'),
                specs=[[{"type": "indicator"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "indicator"}]]
            )
            
            # Network Overview (gauge)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=graph_stats.get('total_nodes', 0),
                    title={'text': "Total Papers"},
                    delta={'reference': 0},
                    gauge={'axis': {'range': [None, max(graph_stats.get('total_nodes', 1), 100)]},
                           'bar': {'color': "#3498db"},
                           'steps': [{'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 100], 'color': "gray"}],
                           'threshold': {'line': {'color': "red", 'width': 4},
                                       'thickness': 0.75, 'value': 90}}
                ),
                row=1, col=1
            )
            
            # Centrality Distribution
            if centrality_data.get('pagerank'):
                pagerank_values = list(centrality_data['pagerank'].values())
                fig.add_trace(
                    go.Histogram(x=pagerank_values, name='PageRank', marker_color='#e74c3c'),
                    row=1, col=2
                )
            
            # Top Cited Papers (placeholder - would need paper titles)
            citation_counts = [node.get('citation_count', 0) for node in 
                             [{'citation_count': 0}] * 5]  # Placeholder
            fig.add_trace(
                go.Bar(x=list(range(1, 6)), y=citation_counts, name='Top Papers', marker_color='#f39c12'),
                row=2, col=1
            )
            
            # Network Properties
            fig.add_trace(
                go.Indicator(
                    mode="number",
                    value=graph_stats.get('density', 0),
                    title={'text': "Network Density"},
                    number={'valueformat': '.4f'}
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title_text="Network Metrics Dashboard",
                showlegend=False,
                height=600,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating metrics dashboard: {e}")
            # Return error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating metrics dashboard: {e}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig


def export_graph_data(graph_data: Dict, format: str = 'json') -> str:
    """Export graph data in various formats"""
    try:
        if format.lower() == 'json':
            return json.dumps(graph_data, indent=2)
        elif format.lower() == 'csv':
            # Convert to CSV format
            nodes_df = pd.DataFrame(graph_data.get('nodes', []))
            edges_df = pd.DataFrame(graph_data.get('edges', []))
            
            csv_data = f"# Nodes\n{nodes_df.to_csv(index=False)}\n\n# Edges\n{edges_df.to_csv(index=False)}"
            return csv_data
        else:
            return "Unsupported format. Use 'json' or 'csv'."
            
    except Exception as e:
        return f"Error exporting data: {e}"


def create_sample_graph_data() -> Dict:
    """Create sample graph data for testing"""
    return {
        'nodes': [
            {'id': '10.1000/1', 'label': 'Sample Paper 1', 'title': 'Sample Paper 1', 'year': 2020, 'citation_count': 10, 'group': 'root'},
            {'id': '10.1000/2', 'label': 'Sample Paper 2', 'title': 'Sample Paper 2', 'year': 2019, 'citation_count': 15, 'group': 'reference'},
            {'id': '10.1000/3', 'label': 'Sample Paper 3', 'title': 'Sample Paper 3', 'year': 2021, 'citation_count': 8, 'group': 'citation'}
        ],
        'edges': [
            {'from': '10.1000/1', 'to': '10.1000/2', 'arrows': 'to', 'color': '#ff7675'},
            {'from': '10.1000/3', 'to': '10.1000/1', 'arrows': 'to', 'color': '#74b9ff'}
        ],
        'root_doi': '10.1000/1'
    }
