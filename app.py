from flask import Flask, render_template, request, jsonify
from extract_links import extract_links_from_url
from filter_links import filter_links_by_substring, filter_links_by_multiple_substrings

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
def extract():
    try:
        data = request.get_json()
        url = data.get('url', '')
        filter_text = data.get('filter', '')
        
        if not url:
            return jsonify({'error': 'URL requise'}), 400
        
        # Extraire les liens
        links = extract_links_from_url(url)
        
        # Filtrer si nécessaire
        if filter_text:
            links = filter_links_by_substring(links, filter_text)
        
        return jsonify({
            'success': True,
            'count': len(links),
            'links': links
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Artify Link Extractor')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    
    app.run(debug=True, port=args.port)

