from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import redirect, url_for
from pytube import YouTube
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    selected_quality = request.form['selected_quality']

    try:
        yt = YouTube(url)
        selected_stream = yt.streams.get_by_itag(selected_quality)

        destination = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(destination, exist_ok=True)

        out_file = selected_stream.download(output_path=destination)

        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3' if selected_stream.includes_audio_track else out_file
        os.rename(out_file, new_file)

        # Redirect to a new page after successful download
        return redirect(url_for('download_success', title=yt.title))

    except Exception as e:
        return render_template('index.html', error=str(e))

@app.route('/download/success/<title>')
def download_success(title):
    return render_template('download_success.html', title=title)
    
@app.route('/video-info')
def video_info():
    url = request.args.get('url')
    download_type = request.args.get('download_type', 'video')
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(only_audio=(download_type == 'audio'))

        video_info = {
            'title': yt.title,
            'duration': yt.length,
            'thumbnail': yt.thumbnail_url,
            'streams': [{
                'itag': stream.itag,
                'resolution': stream.resolution,
                'abr': stream.abr,
                'filesize': f"{round(stream.filesize / (1024 * 1024), 2)} MB"
            } for stream in streams]
        }
        return jsonify(video_info)
    except Exception as e:
        return jsonify({'error': str(e)})

# if __name__ == '__main__':
#     app.run(debug=True)
