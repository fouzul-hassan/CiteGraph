# 📚 CiteGraph - Research Citation Visualization Tool

**CiteGraph** is a comprehensive research assistant that visualizes citation networks and shows how research fields evolve over time. Built with Streamlit, it provides interactive citation graphs, timeline-based storytelling, and advanced network analytics.

## 🚀 Features

### Core Functionality
- **🔍 DOI Input & Fetching**: Enter any DOI to fetch paper metadata from CrossRef API
- **🕸️ Interactive Citation Graph**: Visualize connections between papers using NetworkX and pyvis
- **📈 Knowledge Evolution Timeline**: See how research fields develop over time with Plotly charts
- **🔍 Advanced Search & Filter**: Filter by year, citation count, and graph depth
- **💾 Export & Share**: Download graphs and data in JSON/CSV formats

### Advanced Analytics
- **📊 Network Metrics**: Density, diameter, clustering coefficient, connected components
- **🎯 Centrality Measures**: PageRank, betweenness, in/out-degree centrality
- **🏘️ Community Detection**: Identify research clusters and communities
- **📈 Citation Distribution**: Histograms and statistical analysis
- **🎨 Interactive Visualizations**: Zoom, pan, and explore networks

### Data Management
- **📚 SQLite Storage**: Local caching and persistence for offline access
- **🔄 Smart Caching**: Efficient data retrieval and storage
- **📋 Paper Metadata**: Complete paper information including abstracts and keywords
- **🔗 Relationship Tracking**: Citations, references, and author relationships

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Database**: SQLite (local storage and caching)
- **Graph Processing**: NetworkX (graph algorithms and analysis)
- **Visualization**: pyvis (interactive networks), Plotly (charts and dashboards)
- **Data Processing**: Pandas, NumPy
- **API Integration**: CrossRef API (free, no key required)

## 📋 Requirements

- Python 3.10+
- Streamlit
- NetworkX
- pyvis
- Plotly
- Pandas
- NumPy
- Requests
- SQLite3 (built-in)

## 🚀 Installation & Setup

### 1. Clone or Download
```bash
# If using git
git clone <repository-url>
cd citegraph

# Or download and extract the files
```

### 2. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or install individually
pip install streamlit networkx pyvis plotly pandas numpy requests
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Access the App
Open your browser and navigate to: `http://localhost:8501`

## 📁 Project Structure

```
citegraph/
├── app.py              # Main Streamlit application
├── db.py               # SQLite database operations
├── graph_utils.py      # Graph building and visualization
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── citegraph.db        # SQLite database (created automatically)
```

## 🎯 Usage Guide

### Getting Started
1. **Launch the App**: Run `streamlit run app.py`
2. **Enter a DOI**: Use the sidebar to input a DOI (e.g., `10.1038/nature12373`)
3. **Fetch Data**: Click "Fetch & Visualize" to process the DOI
4. **Explore**: Use the interactive visualizations to explore the citation network

### Understanding the Interface

#### 📄 Paper Information
- **Title, Authors, Journal**: Basic paper metadata
- **Abstract**: Paper summary and description
- **Keywords**: Research topics and themes
- **Metrics**: Citation count, reference count, publication year

#### 🕸️ Citation Network
- **Root Node**: The input paper (red, larger size)
- **Reference Nodes**: Papers this paper cites (orange)
- **Citation Nodes**: Papers that cite this paper (blue)
- **Interactive Controls**: Zoom, pan, drag nodes, hover for details

#### 📈 Knowledge Evolution Timeline
- **Year Distribution**: Papers published per year
- **Trend Analysis**: Visual representation of research growth
- **Interactive Charts**: Hover for detailed information

#### 📊 Network Metrics
- **Total Papers**: Number of nodes in the network
- **Total Connections**: Number of edges/relationships
- **Network Density**: How connected the network is
- **Connected Components**: Number of separate sub-networks

### Advanced Features

#### 🔍 Filtering Options
- **Year Range**: Filter papers by publication year
- **Citation Count**: Show only papers with minimum citations
- **Graph Depth**: Control how far to explore the network

#### 📊 Export Options
- **Graph Data**: Export network structure as JSON/CSV
- **Timeline Data**: Export year-by-year paper counts
- **Paper List**: Export detailed paper information

## 🔧 Configuration

### Customization Options
- **Graph Physics**: Adjust network layout and behavior
- **Visual Styling**: Modify colors, sizes, and layouts
- **Data Sources**: Connect to different APIs or databases
- **Performance**: Optimize for large networks

### Environment Variables
```bash
# Optional: Set custom database path
export CITEGRAPH_DB_PATH=/path/to/custom/database.db

# Optional: Set CrossRef API rate limits
export CROSSREF_RATE_LIMIT=1000
```

## 📚 API Integration

### CrossRef API
- **Endpoint**: `https://api.crossref.org/works/{doi}`
- **Rate Limit**: 500 requests per hour (free tier)
- **Data**: Paper metadata, citations, references
- **Authentication**: Not required for basic usage

### Example API Response
```json
{
  "DOI": "10.1038/nature12373",
  "title": ["Paper Title"],
  "author": [{"given": "John", "family": "Doe"}],
  "published-print": {"date-parts": [[2020]]},
  "reference-count": 25,
  "is-referenced-by-count": 45
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Install missing packages
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

#### 2. Database Errors
```bash
# Remove corrupted database
rm citegraph.db

# Restart the application
streamlit run app.py
```

#### 3. Network Visualization Issues
```bash
# Check pyvis installation
pip install pyvis --upgrade

# Clear browser cache
# Restart Streamlit
```

#### 4. Performance Issues
- **Large Networks**: Use filtering options to reduce complexity
- **Memory Usage**: Limit graph depth and node count
- **Rendering**: Allow time for large networks to load

### Performance Tips
- **Limit Graph Depth**: Use depth 1-2 for large networks
- **Apply Filters**: Use year and citation filters to reduce complexity
- **Cache Results**: Database automatically caches fetched data
- **Batch Processing**: Process multiple DOIs sequentially

## 🔮 Future Enhancements

### Planned Features
- **🔍 Advanced Search**: Full-text search across papers
- **📊 Comparative Analysis**: Compare multiple research areas
- **🎬 Animation**: Animated timeline showing knowledge evolution
- **🤖 AI Integration**: Smart paper recommendations
- **📱 Mobile Support**: Responsive design for mobile devices

### Community Contributions
- **New Visualization Types**: Additional chart and graph types
- **API Integrations**: Support for more academic databases
- **Performance Optimizations**: Faster rendering for large networks
- **UI/UX Improvements**: Better user experience and accessibility

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests if applicable**
5. **Submit a pull request**

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd citegraph

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest

# Start development server
streamlit run app.py
```

## 📞 Support & Community

- **Documentation**: [Streamlit Docs](https://docs.streamlit.io/)
- **NetworkX**: [NetworkX Documentation](https://networkx.org/)
- **Plotly**: [Plotly Python](https://plotly.com/python/)
- **Issues**: Report bugs and request features via GitHub issues

## 🙏 Acknowledgments

- **Streamlit Team**: For the amazing web framework
- **NetworkX Community**: For graph algorithms and analysis
- **CrossRef**: For providing free academic metadata
- **Open Source Community**: For all the supporting libraries

---

**Happy Research Visualization! 🎉**

*CiteGraph - Making Research Connections Visible*
