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

    def create_interactive_network(
        self,
        graph_data: Dict,
        height: str = "600px",
        physics_enabled: bool = True,
        layout: str = "force",
        scale_by_citations: bool = True,
        show_legend: bool = True
    ) -> str:
        """Create an interactive network visualization using pyvis

        Args:
            graph_data: Graph data dict with 'nodes' and 'edges'
            height: Canvas height (e.g., '700px')
            physics_enabled: Toggle physics simulation
            layout: 'force' or 'hierarchical'
            scale_by_citations: Scale node size by citation count
            show_legend: Include a floating legend overlay
        """
        try:
            # Create pyvis network
            net = Network(height=height, width="100%", bgcolor="#ffffff", font_color="#000000")

            # Determine scaling
            max_citations = 0
            if scale_by_citations:
                for node in graph_data.get('nodes', []):
                    max_citations = max(max_citations, node.get('citation_count', 0) or 0)
                max_citations = max_citations or 1

            # Add nodes
            for node in graph_data.get('nodes', []):
                node_id = node['id']
                label = node.get('label', node_id)
                title = node.get('title', '')
                year = node.get('year', '')
                citation_count = node.get('citation_count', 0) or 0
                group = node.get('group', 'default')
                highlighted = node.get('highlighted', False)

                # Base color and size by group
                if group == 'root':
                    color = '#e74c3c'
                    base_size = 22
                    shape = 'diamond'
                elif group == 'citation':
                    color = '#3498db'
                    base_size = 18
                    shape = 'dot'
                elif group == 'reference':
                    color = '#f39c12'
                    base_size = 18
                    shape = 'dot'
                elif group == 'related':
                    color = '#00b894'
                    base_size = 16
                    shape = 'dot'
                elif group == 'expanded_citation':
                    color = '#9b59b6'
                    base_size = 16
                    shape = 'dot'
                elif group == 'most_relevant':
                    color = '#f1c40f'
                    base_size = 20
                    shape = 'star'
                else:
                    color = '#95a5a6'
                    base_size = 14
                    shape = 'dot'

                # Scale by citations
                if scale_by_citations:
                    scaled = base_size + (22 * (citation_count / max_citations))
                    size = max(base_size, min(scaled, 40))
                else:
                    size = base_size

                # Highlighting
                if highlighted:
                    color = '#2ecc71'
                    size = max(size, base_size + 6)
                    shape = 'star'

                # Create hover title
                hover_title = f"Title: {title}\nYear: {year}\nCitations: {citation_count}"

                net.add_node(
                    node_id,
                    label=label,
                    title=hover_title,
                    color=color,
                    size=size,
                    shape=shape
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

            # Configure layout and physics
            if layout == 'hierarchical':
                options = {
                    "layout": {
                        "hierarchical": {
                            "enabled": True,
                            "direction": "UD",
                            "sortMethod": "hubsize",
                            "levelSeparation": 150,
                            "nodeSpacing": 150
                        }
                    },
                    "physics": {
                        "enabled": physics_enabled,
                        "hierarchicalRepulsion": {
                            "centralGravity": 0.0,
                            "springLength": 150,
                            "springConstant": 0.01,
                            "nodeDistance": 200
                        },
                        "solver": "hierarchicalRepulsion",
                        "stabilization": {"iterations": 200}
                    }
                }
            else:
                options = {
                    "physics": {
                        "enabled": physics_enabled,
                        "forceAtlas2Based": {
                            "gravitationalConstant": -60,
                            "centralGravity": 0.01,
                            "springLength": 120,
                            "springConstant": 0.08
                        },
                        "maxVelocity": 60,
                        "minVelocity": 0.1,
                        "solver": "forceAtlas2Based",
                        "timestep": 0.35,
                        "stabilization": {"iterations": 250}
                    }
                }

            # Apply options
            import json as _json
            net.set_options(f"var options = {_json.dumps(options)}")

            # Save to HTML string
            html_string = net.generate_html()

            # Inject legend overlay
            if show_legend:
                legend_html = (
                    "<div style=\"position:fixed; right:16px; bottom:16px; background:rgba(255,255,255,0.9);"
                    "padding:12px 14px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.15);"
                    "font-family:Inter,system-ui,Segoe UI,Roboto,Arial; font-size:13px; z-index:9999;\">"
                    "<div style=\"font-weight:600; margin-bottom:6px;\">Legend</div>"
                    "<div style=\"display:flex; gap:10px; flex-wrap:wrap; max-width:320px;\">"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#e74c3c; border-radius:50%; margin-right:6px;\"></span>Root</span>"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#3498db; border-radius:50%; margin-right:6px;\"></span>Citation</span>"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#f39c12; border-radius:50%; margin-right:6px;\"></span>Reference</span>"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#00b894; border-radius:50%; margin-right:6px;\"></span>Related</span>"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#9b59b6; border-radius:50%; margin-right:6px;\"></span>Expanded</span>"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#f1c40f; border-radius:50%; margin-right:6px;\"></span>Most Relevant</span>"
                    "<span><span style=\"display:inline-block; width:10px; height:10px; background:#2ecc71; border-radius:50%; margin-right:6px;\"></span>Highlighted</span>"
                    "</div></div>"
                )
                if '</body>' in html_string:
                    html_string = html_string.replace('</body>', legend_html + '</body>')

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
    
    def create_network_metrics_dashboard(self, graph_stats: Dict, centrality_data: Dict, nodes: Optional[List[Dict]] = None) -> go.Figure:
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
            
            # Top Cited Papers (use actual nodes if provided)
            top_x = []
            top_y = []
            if nodes:
                try:
                    top_nodes = sorted(nodes, key=lambda n: n.get('citation_count', 0), reverse=True)[:5]
                    top_x = [n.get('label') or n.get('title') or n.get('id') for n in top_nodes]
                    top_y = [n.get('citation_count', 0) for n in top_nodes]
                except Exception:
                    top_x, top_y = list(range(1, 6)), [0]*5
            else:
                top_x, top_y = list(range(1, 6)), [0]*5
            fig.add_trace(
                go.Bar(x=top_x, y=top_y, name='Top Papers', marker_color='#f39c12'),
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
