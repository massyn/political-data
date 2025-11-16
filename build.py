import os
import logging
import jinja2
import markdown
from data import Data

def calculate_scorecard(indicator_data, overlay_data, y_field, direction):
    """Calculate government performance scorecard"""
    if not overlay_data or not direction:
        return []

    governments = overlay_data['data']
    scorecard = []

    # Process governments in reverse (most recent first), up to 5
    for i in range(len(governments) - 1, -1, -1):
        if len(scorecard) >= 5:
            break

        gov = governments[i]
        next_gov = governments[i + 1] if i + 1 < len(governments) else None

        # Find start value (first data point >= government start)
        start_value = None
        for row in indicator_data:
            if row['date'] >= gov['date']:
                try:
                    start_value = float(row[y_field])
                    break
                except (ValueError, KeyError):
                    pass

        # Find end value (last data point < next government, or latest)
        end_value = None
        if next_gov:
            for row in reversed(indicator_data):
                if row['date'] < next_gov['date']:
                    try:
                        end_value = float(row[y_field])
                        break
                    except (ValueError, KeyError):
                        pass
        else:
            try:
                end_value = float(indicator_data[-1][y_field])
            except (ValueError, KeyError):
                pass

        # Only include if we have both values
        if start_value is not None and end_value is not None:
            change = end_value - start_value
            change_pct = (change / start_value * 100) if start_value != 0 else 0

            # Determine status based on direction
            if direction == 'higher_is_better':
                if change > 0.01:
                    status, status_class, status_icon = 'Improved', 'table-success', '▲'
                elif change < -0.01:
                    status, status_class, status_icon = 'Worsened', 'table-danger', '▼'
                else:
                    status, status_class, status_icon = 'No Change', 'table-warning', '−'
            else:  # lower_is_better
                if change < -0.01:
                    status, status_class, status_icon = 'Improved', 'table-success', '▼'
                elif change > 0.01:
                    status, status_class, status_icon = 'Worsened', 'table-danger', '▲'
                else:
                    status, status_class, status_icon = 'No Change', 'table-warning', '−'

            scorecard.append({
                'name': gov['value'],
                'party': gov['party'],
                'colour': gov['colour'],
                'date': gov['date'],
                'start_value': start_value,
                'end_value': end_value,
                'change': change,
                'change_pct': change_pct,
                'status': status,
                'status_class': status_class,
                'status_icon': status_icon
            })

    return scorecard

def render_jinja(template,output,**KW):
    os.makedirs(os.path.dirname(output),exist_ok = True)
    template_dir = 'templates'
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    tmpl = env.get_template(template)
    result = tmpl.render(**KW)
    print(f"Writing {output}")
    with open(output,'wt',encoding='utf-8') as q:
        q.write(result)

def render_markdown_page(md_file, output_file, page_id, page_title):
    """Read markdown file, convert to HTML, and render using page template"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'codehilite', 'tables'])

    # Render using the page template
    render_jinja('page.jinja', output_file,
                 content=html_content,
                 page_id=page_id,
                 page_title=page_title)

def calculate_government_rag(indicator_data, gov, next_gov, y_field, direction):
    """Calculate RAG status for a specific government period"""
    if not indicator_data or not direction:
        return None

    # Find start value (first data point >= government start)
    start_value = None
    for row in indicator_data:
        if row['date'] >= gov['date']:
            try:
                start_value = float(row[y_field])
                break
            except (ValueError, KeyError):
                pass

    # Find end value (last data point < next government, or latest)
    end_value = None
    if next_gov:
        for row in reversed(indicator_data):
            if row['date'] < next_gov['date']:
                try:
                    end_value = float(row[y_field])
                    break
                except (ValueError, KeyError):
                    pass
    else:
        try:
            end_value = float(indicator_data[-1][y_field])
        except (ValueError, KeyError):
            pass

    if start_value is None or end_value is None:
        return None

    change = end_value - start_value

    # Determine status based on direction
    if direction == 'higher_is_better':
        if change > 0.01:
            status = 'Improved'
        elif change < -0.01:
            status = 'Worsened'
        else:
            status = 'No Change'
    else:  # lower_is_better
        if change < -0.01:
            status = 'Improved'
        elif change > 0.01:
            status = 'Worsened'
        else:
            status = 'No Change'

    return status

def calculate_current_government_rag(indicator_data, overlay_data, y_field, direction):
    """Calculate RAG status for current government"""
    if not overlay_data or not direction or not indicator_data:
        return None

    # Get current government (last one in the list)
    current_gov = overlay_data['data'][-1]

    # Find start value (first data point >= government start)
    start_value = None
    for row in indicator_data:
        if row['date'] >= current_gov['date']:
            try:
                start_value = float(row[y_field])
                break
            except (ValueError, KeyError):
                pass

    # Get latest value
    end_value = None
    try:
        end_value = float(indicator_data[-1][y_field])
    except (ValueError, KeyError):
        pass

    if start_value is None or end_value is None:
        return None

    change = end_value - start_value
    change_pct = (change / start_value * 100) if start_value != 0 else 0

    # Determine status based on direction
    if direction == 'higher_is_better':
        if change > 0.01:
            status, status_icon = 'Improved', '▲'
        elif change < -0.01:
            status, status_icon = 'Worsened', '▼'
        else:
            status, status_icon = 'No Change', '−'
    else:  # lower_is_better
        if change < -0.01:
            status, status_icon = 'Improved', '▼'
        elif change > 0.01:
            status, status_icon = 'Worsened', '▲'
        else:
            status, status_icon = 'No Change', '−'

    return {
        'status': status,
        'status_icon': status_icon,
        'change': change,
        'change_pct': change_pct,
        'government': current_gov['value']
    }

def calculate_government_scorecard_summary(D, jurisdiction, indicators):
    """Calculate summary scorecard for last 5 governments"""
    # Get prime minister data to know the governments
    pm_data = D.result(jurisdiction, 'prime_minister', is_latest=False)
    if not pm_data or not pm_data.get('data'):
        return None

    governments = pm_data['data']
    scorecard = []

    # Process last 5 governments in reverse (most recent first)
    for i in range(len(governments) - 1, max(-1, len(governments) - 6), -1):
        gov = governments[i]
        next_gov = governments[i + 1] if i + 1 < len(governments) else None

        green_count = 0
        amber_count = 0
        red_count = 0

        # Check each indicator
        for indicator in indicators:
            if indicator.get('graph') and indicator['graph'] != False:
                for graph_config in indicator['graph']:
                    if 'direction' in graph_config and 'overlay_metric' in graph_config:
                        # Get full indicator data
                        full_data = D.result(jurisdiction, indicator['id'], is_latest=False)

                        status = calculate_government_rag(
                            full_data['data'],
                            gov,
                            next_gov,
                            graph_config['y'],
                            graph_config['direction']
                        )

                        if status == 'Improved':
                            green_count += 1
                        elif status == 'Worsened':
                            red_count += 1
                        elif status == 'No Change':
                            amber_count += 1

                        break  # Only process first graph config with direction

        # Calculate net score (improved - worsened)
        net_score = green_count - red_count

        scorecard.append({
            'name': gov['value'],
            'party': gov['party'],
            'colour': gov['colour'],
            'date': gov['date'],
            'green': green_count,
            'amber': amber_count,
            'red': red_count,
            'total': green_count + amber_count + red_count,
            'score': net_score
        })

    return scorecard

def main(target):
    D = Data()
    os.makedirs(target,exist_ok=True)

    # Render the static markdown pages
    render_markdown_page('pages/about.md', f'{target}/about.html', 'about', 'About')

    # Render the index page
    render_jinja('index.jinja', f'{target}/index.html', jurisdictions = D.jurisdictions())

    for j in D.jurisdictions():
        # Prepare indicators with RAG status for current government
        indicators_with_rag = []
        for i in D.indicators(j):
            indicator_data = i.copy()

            # Calculate current government RAG if indicator has direction
            if i.get('graph') and i['graph'] != False:
                for graph_config in i['graph']:
                    if 'direction' in graph_config and 'overlay_metric' in graph_config:
                        overlay_id = graph_config['overlay_metric']
                        overlay_data = D.result(j, overlay_id, is_latest=False)

                        # Get full indicator data
                        full_data = D.result(j, i['id'], is_latest=False)

                        rag = calculate_current_government_rag(
                            full_data['data'],
                            overlay_data,
                            graph_config['y'],
                            graph_config['direction']
                        )

                        if rag:
                            indicator_data['rag'] = rag
                        break

            indicators_with_rag.append(indicator_data)

        # Calculate government scorecard summary
        government_scorecard = calculate_government_scorecard_summary(D, j, indicators_with_rag)

        render_jinja('jurisdiction.jinja', f'{target}/{j.lower()}.html',
                    jurisdiction = j, indicators = indicators_with_rag,
                    government_scorecard = government_scorecard)

        for i in D.indicators(j):
            res = D.result(j,i['id'],is_latest=False)

            # Check if any graph has an overlay_metric and fetch that data
            overlay_data = {}
            scorecards = {}
            if res['indicator'].get('graph') and res['indicator']['graph'] != False:
                for graph_config in res['indicator']['graph']:
                    if 'overlay_metric' in graph_config:
                        overlay_id = graph_config['overlay_metric']
                        if overlay_id not in overlay_data:
                            overlay_data[overlay_id] = D.result(j, overlay_id, is_latest=False)

                        # Calculate scorecard if direction is specified
                        if 'direction' in graph_config and graph_config['y'] not in scorecards:
                            scorecards[graph_config['y']] = calculate_scorecard(
                                res['data'],
                                overlay_data[overlay_id],
                                graph_config['y'],
                                graph_config['direction']
                            )

            render_jinja('indicator.jinja', f"{target}/{j.lower()}_{i['id'].lower()}.html",
                        jurisdiction = j, indicator = res, overlay_data = overlay_data, scorecards = scorecards)

if __name__ == '__main__':
    main('./dist')