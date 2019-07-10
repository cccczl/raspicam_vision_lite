import os
import sys
import logging
from flask import Flask, Response, render_template, request, session, redirect, url_for
from .camera import VideoStreamCV2, VideoStreamPiCam
from .interpreter import TFLiteInterpreter
from .stream import gen


logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt=' %I:%M:%S ',
    level="INFO"
)
logger = logging.getLogger(__name__)

basepath = os.path.dirname(__file__)

def create_app():
    app = Flask(__name__)
    
    camera = VideoStreamPiCam()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        model_dir = os.path.join(basepath, 'models')
        logger.info('Fetched model candidates from directory {}'.format(model_dir))
        
        candidates = [d for d in next(os.walk(model_dir))[1] if not d.startswith('.')]
        target = request.form.get("candidates")
        logger.info('Selected model: {}'.format(target))
        return render_template('index.html', candidates=candidates, target=target)


    @app.route('/videostream/<target>', methods=['GET', 'POST'])
    def videostream(target):
        model_path = os.path.join(basepath, 'models', target, '{}.tflite'.format(target))
        label_path = os.path.join(basepath, 'models', target, 'labels.txt')
        model = TFLiteInterpreter(model_path, label_path)
        return Response(gen(camera, model),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
    return app