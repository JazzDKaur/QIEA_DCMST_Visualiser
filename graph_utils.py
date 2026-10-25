import io
import re
import math
import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


def read_csv(source):
    df = pd.read_csv(source, dtype=str).dropna(how='all')
    df.columns = [re.sub(r'[^a-z0-9]', '', str(c).lower()) for c in df.columns]
    return df


def node(value):
    value = str(value).strip()
    if not value or value.lower() == 'nan':
        raise ValueError('Missing vertex identifier.')
    try:
        n = float(value)
        if math.isfinite(n) and n.is_integer():
            return str(int(n))
    except ValueError:
        pass
    return value


def number(value):
    n = float(str(value).replace(',', ''))
    if not math.isfinite(n):
        raise ValueError('Weights must be finite numbers.')
    return n


def endpoints(row, cols):
    a = next((c for c in ['from','source','u','node1','vertex1'] if c in cols), None)
    b = next((c for c in ['to','target','v','node2','vertex2'] if c in cols), None)
    if a and b:
        return node(row[a]), node(row[b])
    if 'edge' in cols:
        parts = re.split(r'\s*[–—−-]\s*', str(row['edge']).strip())
        if len(parts) == 2 and all(parts):
            return node(parts[0]), node(parts[1])
    raise ValueError('Use from,to columns or an Edge column such as 1–13.')


def load_graph(source):
    df = read_csv(source)
    if 'weight' not in df:
        raise ValueError('Graph CSV needs a weight column.')
    graph = nx.Graph()
    rows = {}
    for i, (_, row) in enumerate(df.iterrows(), 1):
        u, v = endpoints(row, df.columns)
        if u == v or graph.has_edge(u, v):
            raise ValueError(f'Graph data row {i}: self-loop or duplicate undirected edge.')
        weight = number(row['weight'])
        graph.add_edge(u, v, weight=weight)
        rows[i] = (u, v, weight)
    if not graph.number_of_edges():
        raise ValueError('Graph CSV is empty.')
    return graph, rows


def load_solution(source, graph, rows):
    df = source.copy() if isinstance(source, pd.DataFrame) else read_csv(source)
    df = df.dropna(how='all')
    df.columns = [re.sub(r'[^a-z0-9]', '', str(c).lower()) for c in df.columns]
    tree = nx.Graph()
    tree.add_nodes_from(graph.nodes)
    errors, records = [], []
    for i, (_, row) in enumerate(df.iterrows(), 1):
        if any(str(x).strip().lower() == 'total' for x in row.values):
            continue
        has_edge = 'edge' in df or any(c in df for c in ['from','source','u','node1','vertex1'])
        row_number = None
        if 'csvrow' in df and pd.notna(row['csvrow']) and str(row['csvrow']).strip():
            n = number(row['csvrow'])
            if not n.is_integer() or int(n) not in rows:
                raise ValueError(f'Solution line {i}: CSV Row is outside the graph edge list.')
            row_number = int(n)
        if has_edge:
            u, v = endpoints(row, df.columns)
        elif row_number is not None:
            u, v, _ = rows[row_number]
        else:
            raise ValueError('Solution needs Edge, from/to, or CSV Row columns.')
        if row_number is not None and {u,v} != set(rows[row_number][:2]):
            errors.append(f'Line {i}: CSV Row {row_number} points to a different edge.')
        if not graph.has_edge(u,v):
            raise ValueError(f'Solution line {i}: edge {u}–{v} is absent from the selected instance.')
        if tree.has_edge(u,v):
            errors.append(f'Line {i}: repeated edge {u}–{v}.')
            continue
        w = graph[u][v]['weight']
        supplied = row.get('weight')
        if supplied is not None and pd.notna(supplied) and not math.isclose(number(supplied), w, rel_tol=1e-9, abs_tol=1e-8):
            errors.append(f'Edge {u}–{v}: solution weight {supplied}; instance weight {w:g}.')
        tree.add_edge(u,v,weight=w)
        records.append({'CSV Row':row_number if row_number is not None else next(k for k, (a,b,_) in rows.items() if {a,b} == {u,v}),'Edge':f'{u}–{v}','Weight':w})
    if not records:
        raise ValueError('Solution CSV contains no edges.')
    return tree, errors, pd.DataFrame(records)


def validate(tree, degree):
    errors = []
    if not nx.is_connected(tree): errors.append('The solution does not connect every instance vertex.')
    if not nx.is_forest(tree): errors.append('The solution contains a cycle.')
    if tree.number_of_edges() != tree.number_of_nodes()-1: errors.append('A spanning tree must contain exactly n−1 edges.')
    excess = [v for v,d in tree.degree if d > degree]
    if excess: errors.append('Degree limit exceeded at vertices: '+', '.join(excess))
    return errors


def plot_graph(tree, title, layout='Spring', seed=42, node_size=650, font_size=10, show_weights=True, size=14):
    if layout == 'Circular': pos = nx.circular_layout(tree)
    elif layout == 'Kamada–Kawai': pos = nx.kamada_kawai_layout(tree, weight=None)
    else: pos = nx.spring_layout(tree, seed=seed, weight=None, iterations=250)
    degrees = sorted(set(dict(tree.degree).values()))
    palette = plt.get_cmap('tab10')
    # Degree 1 blue, degree 2 orange, degree 3 green, etc.; stable across instances.
    colour = {d:palette(max(d-1,0)%10) for d in degrees}
    fig, ax = plt.subplots(figsize=(size, size*.72), facecolor='white')
    nx.draw_networkx_edges(tree,pos,ax=ax,edge_color='#666666',width=1.2)
    nx.draw_networkx_nodes(tree,pos,ax=ax,node_color=[colour[tree.degree(v)] for v in tree],node_size=node_size,edgecolors='#333333',linewidths=1.2)
    nx.draw_networkx_labels(tree,pos,ax=ax,font_size=font_size,font_weight='bold')
    if show_weights:
        nx.draw_networkx_edge_labels(tree,pos,ax=ax,edge_labels={(u,v):f"{d['weight']:g}" for u,v,d in tree.edges(data=True)},font_size=max(5,font_size-1),rotate=False,bbox={'facecolor':'white','edgecolor':'none','alpha':.85,'pad':.3})
    ax.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=colour[d],markeredgecolor='#333333',markersize=10,label=f'Degree {d}') for d in degrees],title='Vertex Degree',loc='upper right')
    ax.set_title(title,fontsize=14,pad=22)
    ax.margins(.15)
    ax.axis('off')
    fig.tight_layout()
    return fig


def export_image(fig, fmt, dpi=200):
    out = io.BytesIO()
    fig.savefig(out,format=fmt,dpi=dpi,bbox_inches='tight',facecolor='white')
    return out.getvalue()


def find_workbook(folder, graph_name):
    """Exact stem first; also accept crd300_graph_edges.csv -> crd300.xlsx."""
    stems = [graph_name.casefold()]
    base = re.sub(r'_graph_edges(?:\(\d+\))?$', '', graph_name, flags=re.I).casefold()
    if base not in stems:
        stems.append(base)
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {'.xlsx', '.xls', '.xlsm'} and not p.name.startswith('~$')] if folder.is_dir() else []
    for stem in stems:
        matches = [p for p in files if p.stem.casefold() == stem]
        if len(matches) > 1:
            raise ValueError('Multiple matching workbooks: ' + ', '.join(p.name for p in matches))
        if matches:
            return matches[0]
    raise ValueError(f'No matching Excel workbook for {graph_name}. Put {graph_name}.xlsx in {folder}.')


def read_degree_sheet(workbook, degree):
    expected = f'D{degree}'
    with pd.ExcelFile(workbook) as excel:
        matches = [s for s in excel.sheet_names if s.strip().upper() == expected]
        if len(matches) != 1:
            raise ValueError(f'Workbook must have one sheet named {expected}. Available sheets: {", ".join(excel.sheet_names)}')
        return pd.read_excel(excel, sheet_name=matches[0], dtype=str).dropna(how='all')


def available_solutions(graph_folder, solution_folder):
    """Return only graphs whose matching workbook has a nonempty degree sheet."""
    available, skipped = {}, []
    graphs = sorted(p for p in graph_folder.iterdir() if p.is_file() and p.suffix.lower() == '.csv') if graph_folder.is_dir() else []
    for graph in graphs:
        try:
            workbook = find_workbook(solution_folder, graph.stem)
            degrees = []
            with pd.ExcelFile(workbook) as excel:
                for degree in (2,3,4,5):
                    matches = [s for s in excel.sheet_names if s.strip().upper() == f'D{degree}']
                    if len(matches) != 1:
                        continue
                    data = pd.read_excel(excel, sheet_name=matches[0], dtype=str).dropna(how='all')
                    # A heading or Total row alone is not a solution.
                    data = data[~data.apply(lambda row: any(str(v).strip().lower() == 'total' for v in row), axis=1)]
                    if not data.empty:
                        degrees.append(degree)
            if degrees:
                available[graph.stem] = {'graph':graph, 'workbook':workbook, 'degrees':degrees}
            else:
                skipped.append(f'{graph.name}: no nonempty D2–D5 solution sheets.')
        except (ValueError, OSError, ImportError, KeyError) as exc:
            skipped.append(f'{graph.name}: {exc}')
    return available, skipped
