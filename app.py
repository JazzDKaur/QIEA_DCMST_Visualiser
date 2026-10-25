from comparison import render_comparison
from pathlib import Path
import matplotlib.pyplot as plt
import streamlit as st
from graph_utils import load_graph, load_solution, validate, plot_graph, export_image, find_workbook, read_degree_sheet, available_solutions

st.set_page_config(page_title='DCMST Visualizer',layout='wide')
st.title('Degree-Constrained Spanning Tree Visualizer')
st.caption('Choose an instance, load its solution, validate the tree, and download the figure.')
ROOT = Path(__file__).resolve().parent
page = st.sidebar.radio('Navigation', ['Graph and solution', 'Benchmark comparison'])
if page == 'Benchmark comparison':
    render_comparison()
else:
    with st.sidebar:
        st.header('Instance and solution')
        folder = Path(st.text_input('Graph folder', str(ROOT/'GraphEdges'))).expanduser()
        solution_folder = Path(st.text_input('Solution folder', str(ROOT/'solution'))).expanduser()
        sources, skipped = available_solutions(folder, solution_folder)
        if not sources:
            st.info('No solutions available. Add a matching Excel workbook with a nonempty D2, D3, D4 or D5 sheet to the solution folder.')
            if skipped:
                with st.expander('File details'):
                    for message in skipped:
                        st.write(message)
            st.stop()
        instance = st.selectbox('Graph',list(sources))
        selected = sources[instance]
        source = selected['graph']
        name = source.stem
        workbook = selected['workbook']
        limit = st.selectbox('Degree',selected['degrees'],key=f'degree_{instance}')
        st.header('Figure settings')
        layout = st.selectbox('Layout',['Spring','Kamada–Kawai','Circular'])
        seed = st.number_input('Layout seed',min_value=0,max_value=2147483647,value=42)
        size = st.slider('Figure width (inches)',8,30,18)
        spacing = st.slider('Drawing scale',1.0,3.0,1.5,0.1,help='Enlarges the exported canvas relative to labels and vertices. The on-screen plot always fits the page width.')
        nodes = st.slider('Vertex size',100,1800,650,50)
        font = st.slider('Label font size',5,18,10)
        weights = st.checkbox('Display edge weights',True)
        dpi = st.selectbox('Download resolution (DPI)',[150,200,300,600],index=2)
    try:
        graph, rows = load_graph(source)
        data = read_degree_sheet(workbook, limit)
        st.caption(f'Solution: {workbook.name} → D{limit}')
        tree, errors, records = load_solution(data,graph,rows)
        errors += validate(tree,int(limit))
        total = sum(d['weight'] for _,_,d in tree.edges(data=True))
        cols = st.columns(4)
        for c,label,value in zip(cols,['Vertices','Solution edges','Total weight','Maximum degree'],[tree.number_of_nodes(),tree.number_of_edges(),f'{total:,.4f}'.rstrip('0').rstrip('.'),max(dict(tree.degree).values())]):
            c.metric(label,value)
        if errors:
            st.error('Validation failed. The figure below shows the supplied edges using instance weights.')
            for e in errors: st.write('• '+e)
        else:
            st.success(f'Valid spanning tree satisfying degree ≤ {limit}.')
        st.caption('Validation checks feasibility only; it does not certify minimum cost. Layouts show graph connectivity, not original geographic coordinates.')
        title = f'{name} | degree limit {limit} | cost {total:g}' + (' | INVALID' if errors else '')
        fig = plot_graph(tree,title,layout,int(seed),nodes,font,weights,size * spacing)
        st.pyplot(fig, width='stretch')
        downloads = st.columns(3)
        for c,fmt,mime in zip(downloads,['png','svg','pdf'],['image/png','image/svg+xml','application/pdf']):
            c.download_button(f'Download {fmt.upper()}',export_image(fig,fmt,dpi),file_name=f'{name}_degree_{limit}.{fmt}',mime=mime)
        plt.close(fig)
    except (ValueError, OSError, KeyError, ImportError) as exc:
        st.error(str(exc))
